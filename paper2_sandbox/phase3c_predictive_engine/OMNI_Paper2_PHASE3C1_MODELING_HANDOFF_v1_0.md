# OMNI Paper-2 — Phase 3C-1 Modeling Handoff (v1.0)

**Purpose.** Hand a cold thread (Claude or ChatGPT) everything needed to run the first
Phase 3C HIGH-vs-AVG benchmark and continue the predictive-engine build — with **no lost
state, no scavenger hunts, and no re-derivation of decisions already made.** Every
provenance anchor, the frozen target, the exact runnable cell, and the known traps are
named explicitly below.

**Why this exists.** The prior handoff omitted the GitHub repo and did not archive the
"3C state/build cell," which left the five runtime objects (`tr, base, venue, dates,
cv_auc`) undefined in the new thread. This document closes both gaps permanently.

---

## 0. ROLES & OPERATING CONTRACT

- **PI:** Courtney Roberts Conrad — directs and decides. GitHub: `crcatcrc`.
- **ChatGPT ("ChatG"):** execution lead.
- **Claude:** auditor + backup; writes paste-ready Colab cells.
- **Standing style:** concise, PhD/publication rigor, no fool's errands, **complete code
  blocks only** (no TODO-stubs handed to the PI), verbatim recovery (never fabricate from
  memory — recover exact code/counts or say it's missing), errors owned cleanly without
  over-apology.

---

## 1. PROVENANCE ANCHORS (name ALL of these in every future handoff)

| Anchor | Value |
|---|---|
| GitHub repo | `github.com/crcatcrc/omni-geometry-mlb` (private) → folder `paper2_sandbox/` |
| OSF | `osf.io/yhxt4` |
| Drive sandbox | `/content/drive/MyDrive/OMNI_PROJECT/paper2_sandbox` |
| Raw matrices | `/content/drive/MyDrive/MLB 2000-no0224 Training Files by System et al` |
| Environment of record | Colab, Python 3.12, numpy 2.0.2, pandas 2.2.2, scikit-learn 1.6.1 |
| Seed | `20260615` |
| Reproducibility script | `phase3a_analysis.py` (contains `build_state()` and `cv_auc`) |

**Anchor matrix** (carries Date / Total Runs Scored / Venue / Time): the G-AZ→H-LON file,
glob `*Cross-System G-AZ to H-LON*.csv`. It is read first by `build_state()` and is the
canonical source for the per-game outcome and metadata.

---

## 2. DATA CONTRACT (oracles — assert these everywhere)

| Quantity | Value |
|---|---|
| Full corpus | 57,635 games, 2000–2024 (2002 excluded) |
| Exploratory partition | **46,152 events / 3,808 dates** |
| Confirmatory partition (SEALED HOLDOUT) | **952 dates** |
| `holdout_manifest_v1_0.csv` | 4,760 dates = 3,808 exploratory + 952 confirmatory *(verified this thread)* |
| 192-feature H-LON origin classes | angle 130 / moon 39 / helio 23 |
| Phase 3A HS∪LS subset | 8,486 (HS 4,103 / LS 4,383) |

---

## 3. FEATURE UNIVERSE (reconciled, frozen, hash-verified — v1.7)

- Full aspect universe: **2,494 features** across 16 coordinate-system-pair matrices
  (frames G-AZ / G-LON / G-RA / H-LON). Prior Phase-3A work used only the **192-feature
  H-LON slice** — one corner of this.
- Coverage-validity is a **separate axis** from characterization-depth.
- Joint candidate pool (characterized ∩ coverage-clean): **423**.
- **Three modeling universes** (QA 15/15 pass):
  - **Universe A = 345** (Tier-A strict baseline)
  - **Universe B = 423** (Tier A+B+C; **A ⊂ B**; the 78-feature increment over A)
  - **Universe C = 510** (representation-development; not first-pass). Invariants: B ∩ C = ∅, B + C = 933.
- Manifests (in `/mnt/project` and the repo): `HS_LS_UNIVERSE_A/B/C_..._v1_7.csv`,
  `HS_LS_MODELING_UNIVERSE_MANIFESTS_QA_v1_7.csv`.
- SHA-256 prefixes: A `572716bd` · B `154c0925` · C `b4befe89` · QA `07dd54df`.
  **Note:** `HS_LS_UNIVERSE_C_..._v1_7_1.csv` is byte-identical to canonical C (`b4befe89`) — delete one copy.

---

## 4. PHASE 3C TARGET — FROZEN (Option 2)

Two **separate binary models** (NOT 3-class softmax). The two AVG reference bands differ
**by design** (matched-buffer construction), which is precisely why two binaries is the
natural implementation.

| Model | Positive | Negative (AVG) | Build order |
|---|---|---|---|
| **HIGH** | Total Runs ≥ 14 | Total Runs ∈ {7, 8} | **FIRST** (cleaner shakedown) |
| **LOW** | Total Runs ≤ 4 | Total Runs ∈ {8, 9} | second, identical machinery |

**Operational combination of the two model outputs:** both say AVG → AVERAGE; one
extreme → that class; both extreme → uncertain/abstain.

**Why Option 2 (14+/4−) over Option 1 (15+/3−)** — decided on **design grounds, not AUC**:
better class balance (0.536/0.560 vs 0.598/0.656), more data on both sides (esp. the weak
LOW side, 14,695 vs 12,543), and buffers still cleanly drop runs 5–7 (no "5-vs-7"
problem). **Target was NOT selected by max astro-AUC** — that guardrail is load-bearing.

### Target oracles (exploratory ∩ regular-season, from the Phase 3C-0 target sweep)

| Band | Count |
|---|---|
| HIGH ≥ 15 | 5,675 |
| **HIGH ≥ 14** | **7,286** ← Option 2 HIGH positive |
| **AVG 7–8** | **8,431** ← Option 2 HIGH negative |
| LOW ≤ 3 | 4,311 |
| **LOW ≤ 4** | **6,463** ← Option 2 LOW positive |
| **AVG 8–9** | **8,232** ← Option 2 LOW negative |

HIGH-model assert: `HIGH=7286`, `AVG=8431`. LOW-model assert (when built): `LOW=6463`,
`AVG=8232` — re-assert these the same way on the LOW pass.

---

## 5. RUNTIME STATE — THE FIVE OBJECTS (this is what broke the last thread)

The benchmark cell needs five objects. **Their names collide with phase3a_analysis.py
variables that mean something completely different.** Build them fresh with their **3C
meanings**; do **not** consume the phase3a versions.

| Object | 3C meaning (what the benchmark needs) | Source | ⚠️ phase3a name collision |
|---|---|---|---|
| `cv_auc` | function: date-grouped 5-fold OOF AUC (median-impute→standardize→logistic; `l1=True`→L1/liblinear@C, `l1=False`→L2) | `phase3a_analysis.py` **line 100** | none — identical, reuse it |
| `tr` | **TOTAL RUNS** per exploratory game (int) | `S.runs` (loaded in `build_state` **lines 166–175** from the G-AZ anchor matrix; returned line 252), then `[S.expl_mask]` | **phase3a `tr` = park TIER** (qcut of per-park HS-rate) — wrong |
| `base` | **regular-season boolean mask** | built from `POSTSEASON_START` (date < cutoff) | **phase3a `base` = scalar AUC** (transient, per-section) — wrong |
| `venue` | park per exploratory game (str) | `S.mpath` "Venue" col, then `[S.expl_mask]` | phase3a `venue` masked to `[hsls]` (8,486); for 3C use `[expl]` (46,152) |
| `dates` | game-date per exploratory game; used as CV **groups** | `S.dates[S.expl_mask]` | phase3a `dates` is full-corpus (57,635); groups = `dates[expl][hsls]` |

**⚠️ KNOWN BUG — do not repeat.** A reconstruction cell produced in the previous-Claude
thread ends by defining `tr = pd.qcut(...park HS-rate...)` (park tier) and
`base = cv_auc(...)` (scalar). Those are the **phase3a meanings** and they break the
benchmark (`ext = tr >= 14` and `base & (...)` both fail). The diagnosis in that thread was
correct (the state was missing); the rebuilt `tr`/`base` at the bottom were not. **Build
`tr`/`base` with the 3C meanings above.**

### Regular-season filter (PI-provided postseason start dates; verified this thread)

Rule: a game is **regular-season iff its date is strictly before that year's postseason
start.** Verified on samples (e.g. 2003-09-29 in, 2003-09-30 out; 2024-10-01 out).

```python
POSTSEASON_START = {2000:"2000-10-03",2001:"2001-10-09",2002:"2002-10-01",2003:"2003-09-30",
 2004:"2004-10-05",2005:"2005-10-04",2006:"2006-10-03",2007:"2007-10-03",2008:"2008-10-01",
 2009:"2009-10-07",2010:"2010-10-06",2011:"2011-09-30",2012:"2012-10-05",2013:"2013-10-01",
 2014:"2014-09-30",2015:"2015-10-06",2016:"2016-10-04",2017:"2017-10-03",2018:"2018-10-02",
 2019:"2019-10-01",2020:"2020-09-29",2021:"2021-10-05",2022:"2022-10-07",2023:"2023-10-03",
 2024:"2024-10-01"}
```

---

## 6. CANONICAL BENCHMARK CELL — Steps 1–2 (paste-ready, complete)

Foundation: `build_state()` (the provenance the team standardized on). Builds the five
objects with 3C meanings, applies the reg-season filter, asserts the oracle, runs park-only.

```python
# =====================================================================
# PHASE 3C-1 | HIGH TARGET BUILD + PARK-ONLY BENCHMARK  (Steps 1-2)
# Foundation: phase3a_analysis.py build_state() (asserts 46,152/3,808).
# Five objects built with their 3C meanings (NOT phase3a's tr=tier / base=scalar):
#   tr    = TOTAL RUNS per exploratory game (int)      <- S.runs[expl]   (lines 166-175)
#   base  = regular-season mask (bool)                 <- postseason cutoffs
#   venue = park per exploratory game (str)            <- S.mpath Venue col
#   dates = game-date per exploratory game (CV groups) <- S.dates[expl]
#   cv_auc= date-grouped 5-fold OOF AUC (function)     <- p3a.cv_auc
# =====================================================================
import importlib.util, numpy as np, pandas as pd
from sklearn.metrics import (average_precision_score, balanced_accuracy_score,
    precision_score, recall_score, confusion_matrix)

P3A_PATH = "/content/drive/MyDrive/OMNI_PROJECT/paper2_sandbox/phase3a_analysis.py"  # confirm path
spec = importlib.util.spec_from_file_location("p3a", P3A_PATH)
p3a = importlib.util.module_from_spec(spec); spec.loader.exec_module(p3a)

S      = p3a.build_state()          # canonical load; asserts partition + feature + class oracles
cv_auc = p3a.cv_auc                 # FUNCTION (target-agnostic)

# ---- exploratory-level objects, 3C meanings ----
expl  = S.expl_mask                                          # 46,152 exploratory rows
tr    = np.asarray(S.runs)[expl].astype(int)                # TOTAL RUNS (Total Runs Scored)
dates = np.asarray(S.dates)[expl]                           # game dates (CV groups)
_v    = pd.read_csv(S.mpath, usecols=lambda c: c.strip() == "Venue")
_v.columns = [c.strip() for c in _v.columns]
venue = pd.Series(_v["Venue"].to_numpy()[expl]).fillna("UNK").astype(str).to_numpy()
assert len(tr) == len(dates) == len(venue) == 46152, "exploratory length mismatch"

# ---- regular-season mask: reg-season iff strictly before that year's postseason start ----
POSTSEASON_START = {2000:"2000-10-03",2001:"2001-10-09",2002:"2002-10-01",2003:"2003-09-30",
 2004:"2004-10-05",2005:"2005-10-04",2006:"2006-10-03",2007:"2007-10-03",2008:"2008-10-01",
 2009:"2009-10-07",2010:"2010-10-06",2011:"2011-09-30",2012:"2012-10-05",2013:"2013-10-01",
 2014:"2014-09-30",2015:"2015-10-06",2016:"2016-10-04",2017:"2017-10-03",2018:"2018-10-02",
 2019:"2019-10-01",2020:"2020-09-29",2021:"2021-10-05",2022:"2022-10-07",2023:"2023-10-03",
 2024:"2024-10-01"}
de   = pd.to_datetime(pd.Series(dates))
cut  = pd.to_datetime(de.dt.year.map(POSTSEASON_START))
base = (de < cut).to_numpy()
print(f"exploratory rows={len(tr)} | regular-season={int(base.sum())} | postseason dropped={int((~base).sum())}")

# ================= STEP 1: HIGH target (Option 2: 14+ vs 7-8) =================
ext = tr >= 14
avg = (tr >= 7) & (tr <= 8)
m   = base & (ext | avg)
y      = ext[m].astype(int)
groups = dates[m]
n_hi, n_avg = int(ext[m].sum()), int(avg[m].sum())
assert n_hi  == 7286, f"HIGH(14+)={n_hi}, expected 7286 -> STOP (label/partition/reg-season mismatch)"
assert n_avg == 8431, f"AVG(7-8)={n_avg}, expected 8431 -> STOP (label/partition/reg-season mismatch)"
print(f"STEP 1 OK | HIGH(14+)={n_hi}  AVG(7-8)={n_avg}  n={len(y)}  "
      f"dates={len(set(groups))}  base_rate={max(y.mean(),1-y.mean()):.3f}")

# ================= STEP 2: park-only benchmark =================
V = pd.get_dummies(pd.Series(venue[m])).to_numpy().astype(float)
auc, proba = cv_auc(V, y, groups, l1=False, return_proba=True)
pred = (proba >= 0.5).astype(int)
print("\n== HIGH 14+ vs AVG 7-8 | PARK-ONLY (venue one-hot, L2, 5-fold date-grouped) ==")
print(f"ROC-AUC : {auc:.4f}   (sweep park_L2 bar: 0.5783)")
print(f"PR-AUC  : {average_precision_score(y, proba):.4f}")
print(f"bal acc : {balanced_accuracy_score(y, pred):.4f}")
print(f"prec(HI): {precision_score(y, pred, zero_division=0):.4f}   rec(HI): {recall_score(y, pred, zero_division=0):.4f}")
print(f"confusion [rows=AVG,HIGH]:\n{confusion_matrix(y, pred)}")
```

**Expected:** park-only ROC-AUC ≈ **0.578** (sweep park_L2 bar for this target). If it
reproduces, labels + folds + venue are wired correctly.

### Fallback cell (no `build_state` dependency)

If `build_state()` hits a path/load issue, a self-contained variant reads the same
columns (`Date`, `Total Runs Scored`, `Venue`) directly from the G-AZ anchor matrix
(glob `*Cross-System G-AZ to H-LON*.csv`), joins `holdout_manifest_v1_0.csv` by date for
`expl`, then runs the identical Step 1–2 logic and hits the same oracle. (Same five-object
construction; only the load differs.)

---

## 7. NEXT STEPS (in order)

1. **Run §6 cell.** Confirm oracle pass + park ≈ 0.578. (PENDING — not yet executed.)
2. **Step 3 — Universe-A geometry only (the ONE piece not yet written).** This needs a
   **broader matrix assembly** than `build_state()` provides: `S.X_full` is only the
   192-feature H-LON slice (384 sin|cos cols). Universe A is **345 features across all 16
   system-pair matrices**. Build `X_A` by loading the 16 matrices, selecting the 345
   `feature_id`s from `HS_LS_UNIVERSE_A_TIER_A_ENGINE_MANIFEST_v1_7.csv`, encoding raw
   directed degree → `[sin | cos]`, aligned to event order, then masked to the same `m`.
   Evaluate on the **same folds**: `cv_auc(X_A, y, groups, l1=True, C=0.1)`. (Write this
   against the live notebook once Step 2 passes — do not fabricate the assembly.)
3. **Step 4 — park + geometry increment.** `cv_auc(np.hstack([V, X_A]), y, groups, ...)`;
   report ΔAUC over the park bar with a paired SE. **Within ~1 SE = null increment.**
4. **LOW model.** Replicate Steps 1–4 on identical machinery with LOW = TR≤4 vs AVG 8–9;
   assert `LOW=6463`, `AVG=8232`.
5. **Freeze the abstention zone on exploratory data BEFORE any holdout access.**
6. Only then touch the sealed holdout (952 confirmatory dates).

---

## 8. STANDING GUARDRAILS (carry into all modeling)

- **Sealed holdout** (952 confirmatory dates) — untouched until target + abstention +
  increment protocol are frozen on exploratory. Load-bearing credibility rule.
- **In-sample lift ≠ predictive.** (Phase 3A 0.80→0.53 collapse was leakage.) Fold-clean
  GroupKFold OOF gates every selection.
- **Park-aware baseline is mandatory.** Park-only ≈ 0.578 on the 3C HIGH target
  (≈ 0.6415 on the old HS/LS target). The live quantity is the **geometry increment over
  the park baseline**, not raw geometry AUC.
- **Raw degree → sin/cos, fold-clean.** Peak-degree / smoothed-lift are **descriptor
  evidence only — NEVER per-event model inputs.**
- **Never select the target (or anything) by max astro-AUC** — that is holdout-tuning one
  level up.
- Descriptor manifests stamp `safe_for_direct_predictive_claim = False`.
- **No new methodology without PI sign-off.**
- BHW/GHL margin track is paused (~0.49).

---

## 9. PHASE 3A REFERENCE (F1–F8: mostly-negative result + park-structure signal)

- Park-only 0.6415 · geometry-only L1 0.5872 · geometry+park 0.6565 (HS/LS target).
- **Parks are not homogeneous** — F6 vindicated the PI's standing prior; treat it as an
  asset to build on, not a defeat.
- The audit voice must **not assert mechanism ahead of evidence** (prior overreaches —
  "it's time-of-day," "helio is just the date," "no park structure" — were caught and
  corrected; guard against this pattern).

---

## 10. CROSS-THREAD COORDINATION

Multiple live threads: this modeling thread (Claude), ChatG (execution), and a
previous-Claude thread (did the state-recovery analysis). When threads disagree:

- The **§6 cell is the agreed canonical path.** It builds `tr`/`base` with 3C meanings.
- Do **not** wire the previous-Claude reconstruction cell into the benchmark (its
  bottom-line `tr`/`base` carry phase3a meanings — see §5 bug note).
- The "3C state cell" referenced in earlier handoffs was a **live Colab cell, never saved
  as a file.** It is now fully reconstructed by §6 — there is nothing left to recover.

---

## 11. ARTIFACT MANIFEST (key files — locations)

In `/mnt/project`, the repo `paper2_sandbox/`, and the Drive sandbox:

- `phase3a_analysis.py` — `build_state()` (lines 131–256), `cv_auc` (line 100). **The
  load + folds source of truth.**
- `HS_LS_UNIVERSE_A/B/C_..._ENGINE_MANIFEST_v1_7.csv` + `..._QA_v1_7.csv` — modeling universes.
- `holdout_manifest_v1_0.csv` — partition (3,808 expl / 952 conf).
- `outcome_labels_manifest_v1_0.csv` — per-event `total_runs` (full corpus 57,635).
- `event_stratum_manifest_v1_0.csv`, `operational_scale_registry_v1_0.csv`,
  `horizontal_feature_registry_v1_0.csv`.
- `OMNI_Paper2_Feature_Universe_Inventory_Writeup_v1_0.md` — full feature-universe write-up.
- `PHASE3A_FINDINGS_LOG_v1_1.md`, `exploration_log_phase3a_entry.md` — Phase 3A record.
- **This document** — `OMNI_Paper2_PHASE3C1_MODELING_HANDOFF_v1_0.md`.

---

## 12. OPEN ITEMS FOR THE PI

- Confirm `P3A_PATH` in the §6 cell matches the actual sandbox path.
- Run §6; report park-only AUC + oracle pass/fail.
- (Already locked: Option 2 target; HIGH-first build order; two-binary architecture.)

*End of handoff v1.0. Nothing about the runtime state, the target, or the data contract is
left implicit — if it is not in this document, it does not block the benchmark.*
