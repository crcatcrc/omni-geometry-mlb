#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
phase3a_analysis.py
===================
OMNI Paper-2 - Phase 3A - Horizontal 360-degree model prototyping (HS-vs-LS).

End-to-end reproduction of the eight locked Phase 3A findings (F1-F8) documented in
PHASE3A_FINDINGS_LOG_v1_1.md. Reads the four raw cross-system aspect matrices, rebuilds
the modeling state, and runs the full exploratory arc: baseline -> sparsity/stability ->
ballpark dominance -> confound controls (season, time-of-day, class-over-park) ->
park-tier stratification and the parked fast-helio lead -> park heterogeneity ->
descriptor correlations. Saves the three artifact CSVs.

SCOPE (held throughout): HS-vs-LS only; horizontal feature families only; EXPLORATORY
partition only; holdout SEALED and never read. No confirmatory or production claims.

DETERMINISM
  seed                 20260615
  cross-validation     GroupKFold(5), grouped by calendar date (no shuffle)
  environment of record  Colab, Python 3.12, numpy 2.0.2, pandas 2.2.2, scikit-learn 1.6.1

DATA CONTRACT (oracles asserted in Section 0)
  matrices             57,635 row-aligned events per file, 192 matched aspect features
  exploratory subset   46,152 events / 3,808 dates
  HS (Total Runs >=16) 4,103   |   LS (Total Runs <=3) 4,383   |   HS|LS = 8,486
  origin classes       angle 130  |  moon 39  |  helio 23

RUNTIME NOTES
  The full script is dominated by three optional blocks (toggle in CONFIG):
    RUN_BAKEOFF        RandomForest leg is ~7 min on Colab CPU.
    RUN_PERMUTATION    120 date-shift OOF refits + 2,000 bootstrap, ~2-3 min.
    RUN_HETEROGENEITY  3 x 2,000 stratified permutations, ~1-2 min.
  With all three off, the script runs in a few minutes and still reproduces F1-F4 + F8.

Author of record: OMNI Paper-2 team (PI + ChatGPT execution + Claude audit). Exploratory.
"""

from __future__ import annotations

import os
import glob
import time
from types import SimpleNamespace

import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.metrics import (
    roc_auc_score, average_precision_score, balanced_accuracy_score,
    precision_score, recall_score, confusion_matrix,
)

# =============================================================================
# CONFIG
# =============================================================================
SEED = 20260615

# Drive layout (Colab). Override here if running elsewhere.
DRIVE_ROOT   = "/content/drive/MyDrive"
MATRIX_DIR   = os.path.join(DRIVE_ROOT, "MLB 2000-no0224 Training Files by System et al")
SANDBOX_DIR  = os.path.join(DRIVE_ROOT, "OMNI_PROJECT", "paper2_sandbox")

# Kit files (registry + holdout manifest). Found by name under DRIVE_ROOT if not pinned.
REGISTRY_NAME = "horizontal_feature_registry_v1_0.csv"
HOLDOUT_NAME  = "holdout_manifest_v1_0.csv"

# Outcome thresholds and class definitions.
HS_THRESHOLD = 16            # Total Runs >= 16  -> High-Scoring (positive class)
LS_THRESHOLD = 3             # Total Runs <= 3   -> Low-Scoring
ANGLE_ORIGINS = {"Asc", "MC", "VX", "EA"}   # observer-dependent (horizon/meridian)
MOON_ORIGIN   = "MO"
# everything else (Me/Ve heliocentric body-body) -> "helio" (location-independent)

# Sparsity / stability-selection hyperparameters (F1-F2).
L1_C_GRID          = (0.03, 0.1, 0.3)
STABILITY_C        = 0.1
STABILITY_N        = 50      # date-grouped resamples
STABILITY_FRAC     = 0.8     # fraction of dates per resample
STABILITY_THRESH   = 0.6     # selection-frequency cut for the "stable" set

# Optional heavy blocks.
RUN_BAKEOFF        = True     # F1 tree bake-off (RandomForest leg ~7 min)
RUN_PERMUTATION    = True     # F5 date-shift permutation + bootstrap + year-halves
RUN_HETEROGENEITY  = True     # F6/F7 park-heterogeneity stratified permutation
SAVE_ARTIFACTS     = True     # write the three CSVs to SANDBOX_DIR

CV = GroupKFold(5)


# =============================================================================
# SHARED HELPER
# =============================================================================
def cv_auc(Xin, y, groups, l1=True, C=0.1, max_iter=5000, return_proba=False):
    """Date-grouped 5-fold out-of-fold AUC under the standard pipeline.

    Pipeline = median impute -> standardize -> logistic. l1=True uses
    L1/liblinear at C; l1=False uses the default L2 (ridge). Identical to the
    pipeline used in every Phase 3A modeling cell.
    """
    clf = (LogisticRegression(penalty="l1", solver="liblinear", C=C, max_iter=max_iter)
           if l1 else LogisticRegression(max_iter=max(max_iter, 4000)))
    pipe = Pipeline([("imp", SimpleImputer(strategy="median")),
                     ("sc", StandardScaler()),
                     ("clf", clf)])
    proba = cross_val_predict(pipe, Xin, y, groups=groups, cv=CV,
                              method="predict_proba")[:, 1]
    auc = roc_auc_score(y, proba)
    return (auc, proba) if return_proba else auc


def _find(fname, root=DRIVE_ROOT):
    hits = [os.path.join(r, fname) for r, _, fs in os.walk(root) if fname in fs]
    if not hits:
        raise FileNotFoundError(f"{fname} not found under {root}")
    return hits[0]


# =============================================================================
# SECTION 0 - STATE BUILD
# Reads the four raw matrices, encodes raw directed angles as sin/cos, joins the
# holdout partition, derives the HS|LS modeling subset, and builds every object
# the downstream sections consume. All data-contract oracles are asserted here.
# =============================================================================
def build_state():
    print("=" * 78)
    print("SECTION 0 | state build")
    print("=" * 78)

    reg = pd.read_csv(_find(REGISTRY_NAME))
    hld = pd.read_csv(_find(HOLDOUT_NAME))
    feat_set = set(reg.feature_id.astype(str).str.strip())

    patterns = {
        "G-AZ->H-LON":  "*Cross-System G-AZ to H-LON*.csv",
        "G-LON->H-LON": "*Cross-System G-LON to H-LON*.csv",
        "G-RA->H-LON":  "*Cross-System G-RA to H-LON*.csv",
        "H-LON->H-LON": "*H-LON to H-LON*aspect*features*.csv",
    }
    paths = {k: (glob.glob(os.path.join(MATRIX_DIR, pat))[:1] or [None])[0]
             for k, pat in patterns.items()}
    for k, p in paths.items():
        print(f"  {k:12s}: {os.path.basename(p) if p else 'NOT FOUND'}")
    mpath = paths["G-AZ->H-LON"]
    assert mpath, "G-AZ to H-LON matrix not found (it anchors Date/Time/Venue/Total Runs)."

    # ---- read matrices, match registry features, verify row-alignment ----
    date_ref = None
    runs = None
    feat_frames, feat_names = [], []
    t0 = time.time()
    for k, path in paths.items():
        if not path:
            print(f"  skip {k} (missing)")
            continue
        t1 = time.time()
        colmap = {c.strip(): c for c in pd.read_csv(path, nrows=0).columns}
        matched = [s for s in colmap if s in feat_set]
        need = [colmap["Date"]]
        if runs is None and "Total Runs Scored" in colmap:
            need.append(colmap["Total Runs Scored"])
        need += [colmap[s] for s in matched]
        df = pd.read_csv(path, usecols=need)
        df.columns = [c.strip() for c in df.columns]
        d = pd.to_datetime(df["Date"], errors="coerce", format="mixed")
        if date_ref is None:
            date_ref = d
            if "Total Runs Scored" in df.columns:
                runs = df["Total Runs Scored"].to_numpy()
        else:
            if len(d) != len(date_ref) or not (d.values == date_ref.values).all():
                raise RuntimeError(f"row misalignment in {k} - switch to key-join")
        feat_frames.append(df[matched].reset_index(drop=True))
        feat_names += matched
        print(f"  {k:12s}: matched {len(matched):3d} feats | rows {len(df)} | {time.time()-t1:.0f}s")

    print(f"\n  total features matched: {len(feat_names)} | read in {time.time()-t0:.0f}s")
    assert len(feat_names) == 192, f"expected 192 matched features, got {len(feat_names)}"

    # ---- raw directed angles -> sin/cos; X_full is [sin(192) | cos(192)] ----
    ANG = pd.concat(feat_frames, axis=1)
    rad = 2 * np.pi * ANG.values / 360.0
    X_full = np.hstack([np.sin(rad), np.cos(rad)])
    dates = date_ref.dt.strftime("%Y-%m-%d").values

    # ---- join holdout partition by date ----
    hld2 = hld.copy()
    hld2["d"] = pd.to_datetime(hld2["game_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    part = pd.Series(dates).map(dict(zip(hld2["d"], hld2["partition"]))).values

    expl_mask = (part == "exploratory")
    ne, nd = int(expl_mask.sum()), len(set(dates[expl_mask]))
    print(f"\n  exploratory rows={ne}  dates={nd}")
    assert ne == 46152 and nd == 3808, "PARTITION ORACLE MISMATCH"

    # ---- HS|LS modeling subset on the exploratory partition ----
    TR = np.asarray(runs)[expl_mask]
    de = dates[expl_mask]
    Xe = X_full[expl_mask]
    hsls = (TR >= HS_THRESHOLD) | (TR <= LS_THRESHOLD)
    y = (TR[hsls] >= HS_THRESHOLD).astype(int)     # HS=1, LS=0
    groups = de[hsls]
    Xy = Xe[hsls]
    base_rate = max(y.mean(), 1 - y.mean())
    assert len(y) == 8486 and int(y.sum()) == 4103 and int((1 - y).sum()) == 4383, \
        "HS/LS ORACLE MISMATCH"
    nf = len(feat_names)
    PHASE3 = dict(X=Xy, y=y, groups=groups, n_feat=nf, base_rate=base_rate)
    print(f"  HS|LS rows={len(y)}  HS={int(y.sum())} LS={int((1-y).sum())}  "
          f"base_rate={base_rate:.4f}")

    # ---- venue (one-hot) and start-time, re-read from the G-AZ matrix, aligned to y ----
    meta_cols = pd.read_csv(mpath, usecols=lambda c: c.strip() in {"Venue", "Time"})
    meta_cols.columns = [c.strip() for c in meta_cols.columns]
    venue = pd.Series(meta_cols["Venue"].to_numpy()[expl_mask][hsls]).fillna("UNK").astype(str)
    V = pd.get_dummies(venue).to_numpy().astype(float)
    assert venue.nunique() > 20, "unexpectedly few venues - check Venue column"
    print(f"  parks: {venue.nunique()} distinct | park matrix {V.shape}")

    # ---- origin-class map and sin/cos column selector ----
    meta = reg.drop_duplicates("feature_id").copy()
    meta["feature_id"] = meta["feature_id"].astype(str).str.strip()
    meta = meta.set_index("feature_id")

    def origin_class(f):
        o = meta.loc[f.strip(), "origin"]
        return "moon" if o == MOON_ORIGIN else ("angle" if o in ANGLE_ORIGINS else "helio")

    classes = np.array([origin_class(f) for f in feat_names])
    cols_for = lambda fm: np.concatenate([np.where(fm)[0], np.where(fm)[0] + nf])
    counts = {c: int((classes == c).sum()) for c in ("angle", "moon", "helio")}
    print(f"  origin classes: angle {counts['angle']} | moon {counts['moon']} | "
          f"helio {counts['helio']}")
    assert counts == {"angle": 130, "moon": 39, "helio": 23}, "CLASS ORACLE MISMATCH"

    Xang = PHASE3["X"][:, cols_for(classes == "angle")]
    Xhel = PHASE3["X"][:, cols_for(classes == "helio")]

    # ---- park tier by descriptive HS-rate (used by F5 stratification) ----
    ven = pd.Series(np.asarray(venue))
    park_hs = pd.Series(y).groupby(ven.values).mean()
    tier = pd.qcut(ven.map(park_hs), 3, labels=["low", "neutral", "high"]).to_numpy()

    return SimpleNamespace(
        reg=reg, hld=hld, hld2=hld2, mpath=mpath, feat_names=feat_names, meta=meta,
        ANG=ANG, X_full=X_full, dates=dates, date_ref=date_ref, runs=runs,
        expl_mask=expl_mask, hsls=hsls, PHASE3=PHASE3, nf=nf,
        venue=venue, V=V, classes=classes, cols_for=cols_for,
        Xang=Xang, Xhel=Xhel, tier=tier,
    )


# =============================================================================
# SECTION 1 (F1) - clean baseline, tree bake-off, sparsity, support gate
#   Reproduces: logistic 0.5768; HGB 0.5611, RF 0.5466; support-gated 0.5774;
#   L1 C=0.03/0.1/0.3 -> 0.5832/0.5872/0.5843 (nonzero 66/114/149 of 384).
# =============================================================================
def section1_baseline_and_sparsity(S):
    print("\n" + "=" * 78)
    print("SECTION 1 (F1) | baseline, bake-off, sparsity, support gate")
    print("=" * 78)
    d = S.PHASE3
    X, y, groups, nf = d["X"], d["y"], d["groups"], d["n_feat"]

    # --- clean raw-angle baseline (L2) ---
    auc, proba = cv_auc(X, y, groups, l1=False, return_proba=True)
    pred = (proba >= 0.5).astype(int)
    print("\n== HS vs LS CLEAN BASELINE - raw-angle sin/cos, 5-fold date-grouped ==")
    print(f"n={len(y)}  angle_features={nf} (x2 sin/cos={X.shape[1]})  base_rate={d['base_rate']:.4f}")
    print(f"ROC-AUC : {auc:.4f}")
    print(f"PR-AUC  : {average_precision_score(y, proba):.4f}")
    print(f"bal acc : {balanced_accuracy_score(y, pred):.4f}")
    print(f"prec(HS): {precision_score(y, pred):.4f}")
    print(f"rec(HS) : {recall_score(y, pred):.4f}")
    print(f"confusion [rows=LS,HS]:\n{confusion_matrix(y, pred)}")

    # --- model bake-off (does nonlinearity help? answer: no) ---
    if RUN_BAKEOFF:
        print("\n-- model bake-off (RandomForest leg is ~7 min) --")
        models = {
            "LogisticRegression": Pipeline([("imp", SimpleImputer(strategy="median")),
                                            ("sc", StandardScaler()),
                                            ("lr", LogisticRegression(max_iter=3000))]),
            "RandomForest":       Pipeline([("imp", SimpleImputer(strategy="median")),
                                            ("rf", RandomForestClassifier(n_estimators=400,
                                                                          n_jobs=-1,
                                                                          random_state=SEED))]),
            "HistGradBoosting":   Pipeline([("imp", SimpleImputer(strategy="median")),
                                            ("gb", HistGradientBoostingClassifier(random_state=SEED))]),
        }
        print(f"{'model':20s} {'ROC-AUC':>8s} {'PR-AUC':>8s} {'bal_acc':>8s}   "
              f"(base_rate={d['base_rate']:.3f})")
        for name, pipe in models.items():
            t0 = time.time()
            pr = cross_val_predict(pipe, X, y, groups=groups, cv=CV,
                                   method="predict_proba")[:, 1]
            prd = (pr >= 0.5).astype(int)
            print(f"{name:20s} {roc_auc_score(y, pr):8.4f} "
                  f"{average_precision_score(y, pr):8.4f} "
                  f"{balanced_accuracy_score(y, prd):8.4f}   [{time.time()-t0:.0f}s]")
    else:
        print("\n-- model bake-off skipped (RUN_BAKEOFF=False) --")

    # --- support gate (inert) + L1 sparsity sweep (dilution test) ---
    r = S.reg.copy()
    r["feature_id"] = r.feature_id.astype(str).str.strip()
    r["lock_succeeded"] = r.lock_succeeded.map({True: True, False: False,
                                                "True": True, "False": False})
    r["sup"] = (r.peak_lift > 1.15) & (r.peak_count >= 30) & (r.lock_succeeded == True)
    supp = set(r[(r.outcome_pole.isin(["HS", "LS"])) & (r.sup)].feature_id)
    keep = [i for i, f in enumerate(S.feat_names) if f in supp]
    colidx = keep + [i + nf for i in keep]
    Xs = X[:, colidx]
    print(f"\nall-192 X={X.shape} | support-gated X={Xs.shape} ({len(keep)} feats)")
    print(f"{'all-192  L2':26s} AUC {cv_auc(X,  y, groups, l1=False):.4f}")
    print(f"{'support-gated L2':26s} AUC {cv_auc(Xs, y, groups, l1=False):.4f}")
    for C in L1_C_GRID:
        pipe = Pipeline([("imp", SimpleImputer(strategy="median")),
                         ("sc", StandardScaler()),
                         ("lr", LogisticRegression(penalty="l1", solver="liblinear",
                                                   C=C, max_iter=5000))])
        pr = cross_val_predict(pipe, X, y, groups=groups, cv=CV,
                               method="predict_proba")[:, 1]
        pipe.fit(X, y)
        nz = int((pipe.named_steps["lr"].coef_ != 0).sum())
        print(f"all-192 L1 C={C:<4}        AUC {roc_auc_score(y, pr):.4f}  "
              f"nonzero {nz}/{X.shape[1]} cols")


# =============================================================================
# SECTION 2 (F2) - stability selection + STABLE_64 feature report
#   Reproduces: 64 features at sel_freq>=0.6; per-class survival helio 16/23,
#   moon 17/39, angle 31/130; support overlap 0.94/0.94 vs 0.89/0.91.
#   Writes STABLE_64_FEATURE_REPORT_v1.csv.
# =============================================================================
def section2_stability(S):
    print("\n" + "=" * 78)
    print("SECTION 2 (F2) | stability selection + STABLE_64 report")
    print("=" * 78)
    d = S.PHASE3
    X, y, groups, nf = d["X"], d["y"], d["groups"], d["n_feat"]

    rng = np.random.default_rng(SEED)
    udates = np.unique(groups)
    sel = np.zeros(X.shape[1])
    coef = np.zeros(X.shape[1])
    for _ in range(STABILITY_N):
        samp = set(rng.choice(udates, size=int(STABILITY_FRAC * len(udates)), replace=False))
        m = np.fromiter((g in samp for g in groups), bool, len(groups))
        pipe = Pipeline([("imp", SimpleImputer(strategy="median")),
                         ("sc", StandardScaler()),
                         ("lr", LogisticRegression(penalty="l1", solver="liblinear",
                                                   C=STABILITY_C, max_iter=5000))])
        pipe.fit(X[m], y[m])
        c = pipe.named_steps["lr"].coef_.ravel()
        sel += (c != 0)
        coef += c
    sel_freq, mean_coef = sel / STABILITY_N, coef / STABILITY_N

    cf = pd.DataFrame({"feature_id": [S.feat_names[i % nf] for i in range(X.shape[1])],
                       "kind": ["sin"] * nf + ["cos"] * nf,
                       "sf": sel_freq, "mc": mean_coef})
    piv = cf.pivot_table(index="feature_id", columns="kind",
                         values=["sf", "mc"], fill_value=0)
    out = pd.DataFrame({
        "feature_id": piv.index,
        "sel_freq": np.maximum(piv[("sf", "sin")], piv[("sf", "cos")]).values,
        "amplitude": np.sqrt(piv[("mc", "sin")] ** 2 + piv[("mc", "cos")] ** 2).values,
    })

    r = S.reg.copy()
    r["feature_id"] = r.feature_id.str.strip()
    r["lock_succeeded"] = r.lock_succeeded.map({True: True, False: False,
                                                "True": True, "False": False})
    r["sup"] = (r.peak_lift > 1.15) & (r.peak_count >= 30) & (r.lock_succeeded == True)
    hs_sup = set(r[(r.outcome_pole == "HS") & r.sup].feature_id)
    ls_sup = set(r[(r.outcome_pole == "LS") & r.sup].feature_id)
    meta = r.drop_duplicates("feature_id").set_index("feature_id")
    oc = lambda o: "moon" if o == MOON_ORIGIN else ("angle" if o in ANGLE_ORIGINS else "helio")
    out["origin_class"] = out.feature_id.map(lambda f: oc(meta.loc[f, "origin"]))
    out["frame_pair"] = out.feature_id.map(lambda f: meta.loc[f, "coordinate_system_pair"])
    out["target_body"] = out.feature_id.map(lambda f: meta.loc[f, "target_body"])
    out["HS_sup"] = out.feature_id.isin(hs_sup)
    out["LS_sup"] = out.feature_id.isin(ls_sup)
    out["seasonal_candidate"] = out.target_body.eq("Ear")
    out["slow_target"] = out.target_body.isin({"Ear", "NE", "PL", "UR", "SA"})
    out = out.sort_values("sel_freq", ascending=False).reset_index(drop=True)

    STABLE = out[out.sel_freq >= STABILITY_THRESH].sort_values(
        "amplitude", ascending=False).reset_index(drop=True)
    print(f"\nstably-selected (sel_freq>={STABILITY_THRESH}): {len(STABLE)} / 192\n")

    t = out.groupby("origin_class").agg(stable=("sel_freq", lambda s: (s >= STABILITY_THRESH).sum()),
                                        pop=("sel_freq", "size"))
    t["rate"] = (t["stable"] / t["pop"]).round(2)
    print("per-class survival rate (stable/pop):")
    print(t.to_string())
    print("\npredictive WEIGHT by class (amplitude) - where signal actually sits:")
    print(STABLE.groupby("origin_class").amplitude.agg(["count", "sum", "mean", "max"]).round(3).to_string())
    print(f"\nsupport overlap (stable): HS_sup {STABLE.HS_sup.mean():.2f}  LS_sup {STABLE.LS_sup.mean():.2f}"
          f"   (all-192: HS {out.HS_sup.mean():.2f}  LS {out.LS_sup.mean():.2f})")
    print("\nframe-pair among stable:", STABLE.frame_pair.value_counts().to_dict())

    if SAVE_ARTIFACTS:
        _save(STABLE, "STABLE_64_FEATURE_REPORT_v1.csv")
    return out, STABLE


# =============================================================================
# SECTION 3 (F3) - ballpark dominance
#   Reproduces: park-only 0.6415; geometry-only 0.5872; geometry+park 0.6565.
# =============================================================================
def section3_park(S):
    print("\n" + "=" * 78)
    print("SECTION 3 (F3) | ballpark dominance")
    print("=" * 78)
    d = S.PHASE3
    X, y, groups = d["X"], d["y"], d["groups"]
    V = S.V
    a_park = cv_auc(V, y, groups, l1=False)
    a_geo = cv_auc(X, y, groups, l1=True)
    a_gp = cv_auc(np.hstack([X, V]), y, groups, l1=True)
    print(f"{'park only (venue one-hot, L2)':32s} AUC {a_park:.4f}")
    print(f"{'geometry only (L1)':32s} AUC {a_geo:.4f}")
    print(f"{'geometry + park (L1)':32s} AUC {a_gp:.4f}")
    print(f"\nD sky beyond park = {a_gp - a_park:+.4f}")
    print(f"D park beyond sky = {a_gp - a_geo:+.4f}")


# =============================================================================
# SECTION 4 (F4) - confound controls: season, class-over-park, time-of-day
#   Reproduces: calendar-only 0.5132, geo+calendar 0.5866, drop-Earth -0.0015;
#   class-over-park helio +0.0036 / moon -0.0052 / angle +0.0201;
#   park+time 0.6392, angle-over-park+time +0.0135, helio-over +0.0025.
# =============================================================================
def section4_confounds(S):
    print("\n" + "=" * 78)
    print("SECTION 4 (F4) | season, class-over-park, time-of-day controls")
    print("=" * 78)
    d = S.PHASE3
    X, y, groups, nf = d["X"], d["y"], d["groups"], d["n_feat"]
    V, classes, cols_for = S.V, S.classes, S.cols_for
    reg = S.reg

    # ---- F4a: season (calendar) control ----
    print("\n-- season control --")
    doy = pd.to_datetime(pd.Series(groups)).dt.dayofyear.to_numpy()
    ang = 2 * np.pi * doy / 365.25
    CAL = np.column_stack([np.sin(ang), np.cos(ang), np.sin(2 * ang), np.cos(2 * ang)])
    ear_feats = set(reg.loc[reg.target_body == "Ear", "feature_id"].str.strip())
    ear_idx = [i for i, f in enumerate(S.feat_names) if f.strip() in ear_feats]
    ear_cols = set(ear_idx) | {i + nf for i in ear_idx}
    X_noEar = X[:, [j for j in range(X.shape[1]) if j not in ear_cols]]
    a_cal = cv_auc(CAL, y, groups, l1=False)
    a_geo = cv_auc(X, y, groups, l1=True)
    a_noear = cv_auc(X_noEar, y, groups, l1=True)
    a_both = cv_auc(np.hstack([X, CAL]), y, groups, l1=True)
    print(f"{'calendar only (day-of-year, L2)':36s} AUC {a_cal:.4f}")
    print(f"{'geometry all-192 (L1)':36s} AUC {a_geo:.4f}")
    print(f"{'geometry minus Earth-target (L1)':36s} AUC {a_noear:.4f}")
    print(f"{'geometry + calendar (L1)':36s} AUC {a_both:.4f}")
    print(f"  D drop-Earth          = {a_noear - a_geo:+.4f}")
    print(f"  D sky beyond calendar = {a_both - a_cal:+.4f}")
    print(f"  D calendar beyond sky = {a_both - a_geo:+.4f}")

    # ---- F4b: which class adds over park (helio is the clean-celestial column) ----
    print("\n-- class-over-park decomposition --")
    a_park = cv_auc(V, y, groups, l1=False)
    print(f"{'park only (L2)':34s} AUC {a_park:.4f}")
    for nm, m in [("helio (loc-indep, 23)", classes == "helio"),
                  ("moon (39)", classes == "moon"),
                  ("angle (loc-dep, 130)", classes == "angle")]:
        a = cv_auc(np.hstack([V, X[:, cols_for(m)]]), y, groups, l1=True)
        print(f"{'park + ' + nm:34s} AUC {a:.4f}   D over park = {a - a_park:+.4f}")

    # ---- F4c: time-of-day control (ridge/L2 throughout for clean marginals) ----
    print("\n-- time-of-day control --")
    m2 = pd.read_csv(S.mpath, usecols=lambda c: c.strip() in {"Date", "Total Runs Scored", "Time"})
    m2.columns = [c.strip() for c in m2.columns]
    dts = pd.to_datetime(m2["Date"], errors="coerce", format="mixed").dt.strftime("%Y-%m-%d").values
    em = (pd.Series(dts).map(dict(zip(S.hld2["d"], S.hld2["partition"]))).values == "exploratory")
    TR = m2["Total Runs Scored"].to_numpy()[em]
    hs = (TR >= HS_THRESHOLD) | (TR <= LS_THRESHOLD)
    assert ((TR[hs] >= HS_THRESHOLD).astype(int) == y).all(), "alignment mismatch - STOP"
    ts = pd.Series(m2["Time"].astype(str).str.strip().to_numpy()[em][hs])
    hour = pd.to_datetime(ts, format="%I:%M:%S%p", errors="coerce").dt.hour
    if hour.isna().mean() > 0.5:
        hour = pd.to_datetime(ts, errors="coerce").dt.hour
    print(f"Time parsed: {int(hour.notna().sum())}/{len(hour)} | "
          f"start hours: {sorted(hour.dropna().astype(int).unique())}")
    T = pd.get_dummies(hour.fillna(-1).astype(int)).to_numpy().astype(float)
    Xang = X[:, cols_for(classes == "angle")]
    Xhel = X[:, cols_for(classes == "helio")]
    ap = cv_auc(V, y, groups, l1=False)
    apt = cv_auc(np.hstack([V, T]), y, groups, l1=False)
    apta = cv_auc(np.hstack([V, T, Xang]), y, groups, l1=False)
    apth = cv_auc(np.hstack([V, T, Xhel]), y, groups, l1=False)
    print(f"{'park only':28s} AUC {ap:.4f}")
    print(f"{'park + time':28s} AUC {apt:.4f}")
    print(f"{'park + time + angle':28s} AUC {apta:.4f}")
    print(f"{'park + time + helio':28s} AUC {apth:.4f}")
    print(f"  D time over park        = {apt - ap:+.4f}")
    print(f"  D angle over park+time  = {apta - apt:+.4f}")
    print(f"  D helio over park+time  = {apth - apt:+.4f}")


# =============================================================================
# SECTION 5 (F5) - park-tier stratification, within-neutral controls,
#                  fast/slow helio split, and the date-shift permutation.
#   Reproduces: tier all-geo low/neutral/high 0.5466/0.5912/0.5479;
#   within-neutral park 0.4901 -> +date 0.5192 -> +helio 0.5550 -> +angle 0.5877;
#   fast-helio +0.0356 vs earth-helio +0.0140; permutation null mean +0.0267,
#   95th +0.0454, p ~ 0.30 (PARKED: failure to confirm, not disconfirmation).
# =============================================================================
def section5_tiers_and_parked_lead(S):
    print("\n" + "=" * 78)
    print("SECTION 5 (F5) | tier stratification, within-neutral, fast-helio (PARKED)")
    print("=" * 78)
    d = S.PHASE3
    X, y, groups, nf = d["X"], d["y"], d["groups"], d["n_feat"]
    venue, tier, classes, cols_for = S.venue, S.tier, S.classes, S.cols_for
    Xhel, Xang = S.Xhel, S.Xang

    # ---- tier stratification (all-geo / helio / angle within each park tier) ----
    print("\n-- park-tier stratification --")

    def auc_sub(Xin, mk):
        g = groups[mk]
        if len(np.unique(g)) < 5 or len(np.unique(y[mk])) < 2:
            return np.nan
        return cv_auc(Xin[mk], y[mk], g, l1=True, C=0.1)

    print(f"{'park tier':10s} {'n':>5s} {'HS_rate':>7s} {'all-geo':>8s} {'helio':>7s} {'angle':>7s}")
    for t in ["low", "neutral", "high"]:
        mk = (tier == t)
        print(f"{t:10s} {int(mk.sum()):5d} {y[mk].mean():7.3f} "
              f"{auc_sub(X, mk):8.4f} {auc_sub(Xhel, mk):7.4f} {auc_sub(Xang, mk):7.4f}")

    # ---- within-neutral controls (park dummies + date/era, then helio / angle) ----
    print("\n-- within-neutral controls (park + date/era held fixed) --")
    neut = (tier == "neutral")
    yn, gn = y[neut], groups[neut]
    Vn = pd.get_dummies(pd.Series(np.asarray(venue))[neut]).to_numpy().astype(float)
    gd = pd.to_datetime(pd.Series(np.asarray(groups))[neut])
    doy, yr = gd.dt.dayofyear.to_numpy(), gd.dt.year.to_numpy()
    DATE = np.column_stack([np.sin(2 * np.pi * doy / 365.25),
                            np.cos(2 * np.pi * doy / 365.25),
                            (yr - yr.mean()) / yr.std()])
    Xh, Xa = Xhel[neut], Xang[neut]
    print(f"neutral tier: n={int(neut.sum())}  parks={Vn.shape[1]}  HS_rate={yn.mean():.3f}")
    bp = cv_auc(Vn, yn, gn, l1=False)
    bpd = cv_auc(np.hstack([Vn, DATE]), yn, gn, l1=False)
    bph = cv_auc(np.hstack([Vn, DATE, Xh]), yn, gn, l1=False)
    bpa = cv_auc(np.hstack([Vn, DATE, Xa]), yn, gn, l1=False)
    print(f"{'park (within-neutral)':28s} AUC {bp:.4f}")
    print(f"{'park + date/era':28s} AUC {bpd:.4f}")
    print(f"{'park + date + helio':28s} AUC {bph:.4f}")
    print(f"{'park + date + angle':28s} AUC {bpa:.4f}")
    print(f"  D date/era over park   = {bpd - bp:+.4f}")
    print(f"  D helio over park+date = {bph - bpd:+.4f}")
    print(f"  D angle over park+date = {bpa - bpd:+.4f}")

    # ---- fast vs Earth-target helio within neutral tier ----
    print("\n-- fast (Me/Ve) vs Earth-target helio, within neutral --")
    tgt = np.array([S.meta.loc[f.strip(), "target_body"] for f in S.feat_names])
    fast = (classes == "helio") & (tgt != "Ear")
    earth = (classes == "helio") & (tgt == "Ear")
    print(f"fast inner-planet helio: {int(fast.sum())} | Earth-target helio: {int(earth.sum())}")
    base = cv_auc(np.hstack([Vn, DATE]), yn, gn, l1=False)
    fh = cv_auc(np.hstack([Vn, DATE, X[neut][:, cols_for(fast)]]), yn, gn, l1=False)
    eh = cv_auc(np.hstack([Vn, DATE, X[neut][:, cols_for(earth)]]), yn, gn, l1=False)
    print(f"{'park+date (within-neutral)':36s} AUC {base:.4f}")
    print(f"{'  + fast inner-planet helio (Me/Ve)':36s} AUC {fh:.4f}")
    print(f"{'  + Earth-target helio (seasonal)':36s} AUC {eh:.4f}")
    print(f"  D fast-helio (no mundane analog) = {fh - base:+.4f}")
    print(f"  D earth-helio (seasonal proxy)   = {eh - base:+.4f}")

    if not RUN_PERMUTATION:
        print("\n-- date-shift permutation skipped (RUN_PERMUTATION=False) --")
        return

    # ---- adjudicator: date-shift permutation null + bootstrap CI + year-halves ----
    print("\n-- date-shift permutation (chance-feature floor) --")
    rng = np.random.default_rng(SEED)
    fcols = cols_for(fast)
    H = X[neut][:, fcols]
    PD = np.hstack([Vn, DATE])

    def oof(Xin, yy, gg):
        pipe = Pipeline([("imp", SimpleImputer(strategy="median")),
                         ("sc", StandardScaler()),
                         ("lr", LogisticRegression(max_iter=4000))])
        return cross_val_predict(pipe, Xin, yy, groups=gg, cv=CV,
                                 method="predict_proba")[:, 1]

    gn_arr = np.asarray(gn)
    p_base = oof(PD, yn, gn_arr)
    p_full = oof(np.hstack([PD, H]), yn, gn_arr)
    base_auc = roc_auc_score(yn, p_base)
    true_delta = roc_auc_score(yn, p_full) - base_auc
    print(f"base park+date AUC      {base_auc:.4f}")
    print(f"TRUE  D fast-helio      {true_delta:+.4f}")

    # (1) date-clustered bootstrap CI on D (fixed OOF preds)
    ud = pd.unique(gn_arr)
    idx = {k: np.where(gn_arr == k)[0] for k in ud}
    boot = []
    for _ in range(2000):
        ii = np.concatenate([idx[k] for k in rng.choice(ud, len(ud), replace=True)])
        yy = yn[ii]
        if len(np.unique(yy)) < 2:
            continue
        boot.append(roc_auc_score(yy, p_full[ii]) - roc_auc_score(yy, p_base[ii]))
    lo, hi = np.quantile(boot, [0.025, 0.975])
    print(f"(1) bootstrap 95% CI    [{lo:+.4f}, {hi:+.4f}]")

    # (2) date-shift permutation null = chance-feature floor
    uds = np.array(sorted(ud))
    ndt = len(uds)
    rk = {t: i for i, t in enumerate(uds)}
    dr = np.array([rk[t] for t in gn_arr])
    dmap = {}
    for i, t in enumerate(gn_arr):
        if t not in dmap:
            dmap[t] = H[i]
    Hd = np.stack([dmap[t] for t in uds])
    null = []
    for _ in range(120):
        k = rng.integers(30, ndt - 30)
        null.append(roc_auc_score(yn, oof(np.hstack([PD, Hd[(dr + k) % ndt]]), yn, gn_arr)) - base_auc)
    null = np.array(null)
    pval = (1 + np.sum(null >= true_delta)) / (1 + len(null))
    print(f"(2) permutation null    mean {null.mean():+.4f} | 95th {np.quantile(null, 0.95):+.4f} | p {pval:.3f}")

    # (3) year-half stability
    med = np.median(yr)
    for lab, m in [("early", yr <= med), ("late", yr > med)]:
        ym, gm = yn[m], gn_arr[m]
        if len(np.unique(ym)) < 2:
            continue
        bm = roc_auc_score(ym, oof(PD[m], ym, gm))
        fm = roc_auc_score(ym, oof(np.hstack([PD[m], H[m]]), ym, gm))
        print(f"(3) {lab:5s} years D      {fm - bm:+.4f}  (n={int(m.sum())})")
    print("VERDICT: real lead iff TRUE D > permutation 95th AND CI clears null mean "
          "AND both halves positive. Phase 3A: did NOT clear -> PARKED.")


# =============================================================================
# SECTION 6/7 (F6/F7) - per-park geometry report + park-heterogeneity test
#   Reproduces (F6): geometry SD obs 0.0539 vs chance 0.0386 p~0.002 (~49%);
#   angle obs 0.0567 vs 0.0387 p~0.001 (~53%).  (F7): helio obs ~0.0391 vs
#   0.0394 p~0.47 (0%) - the location-independent control correctly shows none.
#   Writes PARK_GEOMETRY_REPORT_v1.csv.
# =============================================================================
def section67_heterogeneity(S):
    print("\n" + "=" * 78)
    print("SECTION 6/7 (F6/F7) | per-park report + park-heterogeneity test")
    print("=" * 78)
    d = S.PHASE3
    X, y, groups = d["X"], d["y"], d["groups"]
    venue, tier, Xang, Xhel = S.venue, S.tier, S.Xang, S.Xhel

    def oof(Xin):
        pipe = Pipeline([("imp", SimpleImputer(strategy="median")),
                         ("sc", StandardScaler()),
                         ("lr", LogisticRegression(penalty="l1", solver="liblinear",
                                                   C=0.1, max_iter=5000))])
        return cross_val_predict(pipe, Xin, y, groups=groups, cv=CV,
                                 method="predict_proba")[:, 1]

    print("fitting global geometry models (OOF)...")
    p_all, p_ang, p_hel = oof(X), oof(Xang), oof(Xhel)

    # ---- per-park report (global OOF preds evaluated within each park) ----
    ven = pd.Series(np.asarray(venue))
    tr = pd.Series(np.asarray(tier))
    rows = []
    for park, ii in ven.groupby(ven).groups.items():
        ii = np.array(ii)
        yy = y[ii]
        if len(ii) < 150 or len(np.unique(yy)) < 2:
            continue
        nmin = int(min(yy.sum(), len(yy) - yy.sum()))
        g = roc_auc_score(yy, p_all[ii])
        rows.append(dict(park=str(park)[:26], tier=str(tr.iloc[ii[0]]), N=len(ii),
                         HS_rate=round(float(yy.mean()), 3), geo_AUC=round(g, 3),
                         angle_AUC=round(roc_auc_score(yy, p_ang[ii]), 3),
                         helio_AUC=round(roc_auc_score(yy, p_hel[ii]), 3),
                         AUC_SE=round(np.sqrt(g * (1 - g) / max(nmin, 1)), 3)))
    rep = pd.DataFrame(rows).sort_values("geo_AUC", ascending=False)
    print(rep.to_string(index=False))
    se = float(rep.AUC_SE.median())
    print(f"\nmedian per-park AUC_SE ~ {se:.3f}  ->  parks differing by < ~{2*se:.2f} "
          f"geo_AUC are not distinguishable.")
    print("\ngeo_AUC by tier:")
    print(rep.groupby("tier").geo_AUC.agg(["mean", "median", "size"]).round(3).to_string())
    if SAVE_ARTIFACTS:
        _save(rep, "PARK_GEOMETRY_REPORT_v1.csv")

    if not RUN_HETEROGENEITY:
        print("\n-- heterogeneity permutation skipped (RUN_HETEROGENEITY=False) --")
        return p_all, p_ang, p_hel

    # ---- stratified-permutation heterogeneity test ----
    print("\n-- park-heterogeneity test (per-park AUC spread vs chance) --")
    rng = np.random.default_rng(SEED)
    parks = [(k, np.array(ii)) for k, ii in ven.groupby(ven).groups.items()
             if len(ii) >= 150 and len(np.unique(y[np.array(ii)])) > 1]
    K = len(parks)
    npos = np.array([int(y[ii].sum()) for _, ii in parks])
    nneg = np.array([int((1 - y[ii]).sum()) for _, ii in parks])
    hs_i = np.where(y == 1)[0]
    ls_i = np.where(y == 0)[0]

    def fauc(pos, neg):
        a = np.concatenate([pos, neg])
        r = a.argsort().argsort().astype(float) + 1
        return (r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))

    def het(p, nrep=2000):
        obs = np.array([roc_auc_score(y[ii], p[ii]) for _, ii in parks])
        v = obs.var()
        hs, ls = p[hs_i], p[ls_i]
        nullv = np.empty(nrep)
        for b in range(nrep):
            hp, lp = rng.permutation(hs), rng.permutation(ls)
            ci = cj = 0
            a = np.empty(K)
            for j in range(K):
                a[j] = fauc(hp[ci:ci + npos[j]], lp[cj:cj + nneg[j]])
                ci += npos[j]
                cj += nneg[j]
            nullv[b] = a.var()
        lo, hi = np.percentile(np.sqrt(nullv), [2.5, 97.5])
        return (np.sqrt(v), np.sqrt(nullv.mean()), lo, hi,
                (1 + np.sum(nullv >= v)) / (1 + nrep), max(0., (v - nullv.mean()) / v))

    print(f"parks tested: {K} (N>=150)\n")
    for name, p in [("geometry(all)", p_all), ("angle", p_ang), ("helio", p_hel)]:
        so, sn, lo, hi, pv, exc = het(p)
        print(f"{name:14s}  obs SD {so:.4f} | chance SD {sn:.4f} | "
              f"95% null SD [{lo:.4f}, {hi:.4f}] | beyond-chance {100*exc:3.0f}% | p {pv:.3f}")
    print("\nobs SD above the 95% null upper bound => real park-to-park spread. "
          "helio should land inside its null.")
    return p_all, p_ang, p_hel


# =============================================================================
# SECTION 8 (F8) - park descriptor table + descriptor correlations
#   Reproduces: angle_AUC vs HS_rate / extremeness / night_frac / med_hour all
#   |Spearman| <= 0.15, p > 0.4 (heterogeneity not explained by obvious descriptors).
#   Writes PARK_DESCRIPTOR_TABLE_v1.csv.
# =============================================================================
def section8_descriptors(S, oof_preds=None):
    print("\n" + "=" * 78)
    print("SECTION 8 (F8) | park descriptor table + correlations")
    print("=" * 78)
    from scipy.stats import pearsonr, spearmanr
    d = S.PHASE3
    y, groups = d["y"], d["groups"]
    venue = S.venue

    if oof_preds is None:
        def _o(Xin):
            pipe = Pipeline([("imp", SimpleImputer(strategy="median")),
                             ("sc", StandardScaler()),
                             ("lr", LogisticRegression(penalty="l1", solver="liblinear",
                                                       C=0.1, max_iter=5000))])
            return cross_val_predict(pipe, Xin, y, groups=groups, cv=CV,
                                     method="predict_proba")[:, 1]
        p_all, p_ang, p_hel = _o(d["X"]), _o(S.Xang), _o(S.Xhel)
    else:
        p_all, p_ang, p_hel = oof_preds

    # start-time descriptors, aligned to the 8,486 HS|LS rows
    m2 = pd.read_csv(S.mpath, usecols=lambda c: c.strip() in {"Date", "Total Runs Scored", "Time"})
    m2.columns = [c.strip() for c in m2.columns]
    dts = pd.to_datetime(m2["Date"], errors="coerce", format="mixed").dt.strftime("%Y-%m-%d").values
    em = (pd.Series(dts).map(dict(zip(S.hld2["d"], S.hld2["partition"]))).values == "exploratory")
    TRt = m2["Total Runs Scored"].to_numpy()[em]
    hst = (TRt >= HS_THRESHOLD) | (TRt <= LS_THRESHOLD)
    assert ((TRt[hst] >= HS_THRESHOLD).astype(int) == y).all(), "time alignment mismatch - STOP"
    ts = pd.Series(m2["Time"].astype(str).str.strip().to_numpy()[em][hst])
    hour = pd.to_datetime(ts, format="%I:%M:%S%p", errors="coerce").dt.hour
    if hour.isna().mean() > 0.5:
        hour = pd.to_datetime(ts, errors="coerce").dt.hour
    hour = hour.to_numpy(dtype=float)
    print(f"start hour parsed: {int(np.isfinite(hour).sum())}/{len(hour)}")

    ven = pd.Series(np.asarray(venue))
    sef = lambda a, np_, nn: float(np.sqrt(a * (1 - a) / max(min(np_, nn), 1)))
    rows = []
    for park, ii in ven.groupby(ven).groups.items():
        ii = np.array(ii)
        yy = y[ii]
        if len(ii) < 150 or len(np.unique(yy)) < 2:
            continue
        npos = int(yy.sum())
        nneg = len(yy) - npos
        ga = roc_auc_score(yy, p_all[ii])
        aa = roc_auc_score(yy, p_ang[ii])
        ha = roc_auc_score(yy, p_hel[ii])
        hh = hour[ii]
        hh = hh[np.isfinite(hh)]
        rows.append(dict(park=str(park)[:26], N=len(ii), HS_rate=round(float(yy.mean()), 3),
                         geo_AUC=round(ga, 3), angle_AUC=round(aa, 3), helio_AUC=round(ha, 3),
                         angle_SE=round(sef(aa, npos, nneg), 3),
                         night_frac=round(float(np.mean(hh >= 18)), 3) if len(hh) else np.nan,
                         med_hour=round(float(np.median(hh)), 1) if len(hh) else np.nan))
    tab = pd.DataFrame(rows).sort_values("angle_AUC", ascending=False)
    print(tab.to_string(index=False))
    if SAVE_ARTIFACTS:
        _save(tab, "PARK_DESCRIPTOR_TABLE_v1.csv")

    # descriptor correlations (does any obvious park descriptor explain angle_AUC?)
    print("\n-- descriptor correlations --")
    t = tab.copy()
    t["HS_extremeness"] = (t["HS_rate"] - 0.5).abs()
    desc = ["HS_rate", "HS_extremeness", "night_frac", "med_hour"]
    print(f"n={len(t)} parks | AUCs noisy (per-park SE ~0.05) -> only |r|>~0.4 is even suggestive\n")
    for outc in ["angle_AUC", "geo_AUC"]:
        print(f"== {outc} ==")
        for dcol in desc:
            m = t[[outc, dcol]].dropna()
            pr, pp = pearsonr(m[outc], m[dcol])
            sr, sp = spearmanr(m[outc], m[dcol])
            print(f"  {dcol:15s} pearson {pr:+.2f} (p={pp:.2f}) | spearman {sr:+.2f} (p={sp:.2f})")
        print()


# =============================================================================
# Artifact saving
# =============================================================================
def _save(df, fname):
    try:
        os.makedirs(SANDBOX_DIR, exist_ok=True)
        p = os.path.join(SANDBOX_DIR, fname)
        df.to_csv(p, index=False)
        print(f"saved: {p}")
    except Exception as e:
        print(f"save skipped ({fname}): {e}")


# =============================================================================
# MAIN
# =============================================================================
def main():
    # In Colab, mount Drive first if needed.
    try:
        from google.colab import drive  # noqa
        if not os.path.ismount("/content/drive"):
            drive.mount("/content/drive")
    except Exception:
        pass

    S = build_state()
    section1_baseline_and_sparsity(S)        # F1
    section2_stability(S)                    # F2
    section3_park(S)                         # F3
    section4_confounds(S)                    # F4
    section5_tiers_and_parked_lead(S)        # F5
    oof_preds = section67_heterogeneity(S)   # F6 / F7
    section8_descriptors(S, oof_preds)       # F8

    print("\n" + "=" * 78)
    print("DONE | Phase 3A reproduction complete. Holdout untouched. Exploratory only.")
    print("=" * 78)


if __name__ == "__main__":
    main()
