"""
OMNI Paper 2 Sandbox — Tier 1 Step 2c: local conditional-rate engine (v2).

Direct extension of the Paper 1 lift framework into the Paper 2 outcome
contrasts (HS, LS, BHW, GHL) and stratification axes (all_exploratory,
RS, PS). The Paper 1 instruments — degree-binned conditional rates,
lift relative to baseline, engine-protocol circular smoothing — are
preserved unchanged.

The one new quantity is the local gradient. Two forms are computed:
  PRIMARY:   dRate/dθ — change in outcome probability per degree.
             Directly interpretable as same-day discrimination sensitivity.
  SECONDARY: dLift/dθ = (1/baseline) × dRate/dθ — normalized form,
             useful for cross-class comparison on a common scale.

Both 3° and 5° engine-protocol smoothing windows are computed in parallel
so that peaks observed at both scales can be distinguished from peaks
visible at only one (a stability check, not a significance test).

Charter §1, §4.3, §5.1, §5.2 are the authoritative references.
Tier 1 Step 2c artifact per Charter §4.1.

Asc × MO is the CALIBRATION feature for engine continuity validation;
it is not the scientific target. The target sequence after calibration is
Asc × SU, Asc × VE, Asc × ME, then cross-coordinate constructions.
"""

from pathlib import Path
import hashlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- Paths ------------------------------------------------------------------
SANDBOX_ROOT  = Path("/content/drive/MyDrive/OMNI_PROJECT/paper2_sandbox")
GATE_DIR      = SANDBOX_ROOT / "CONFIRMATORY_GATE"
SENTINEL      = GATE_DIR / "sandbox_seal_v1_0.lock"
PER_EVENT_DIR = Path("/content/drive/MyDrive/OMNI_PROJECT/workspace/per_event_features")
STRATUM_PATH  = SANDBOX_ROOT / "event_stratum_manifest_v1_0.csv"
HOLDOUT_PATH  = SANDBOX_ROOT / "holdout_manifest_v1_0.csv"
LABELS_PATH   = SANDBOX_ROOT / "outcome_labels_manifest_v1_0.csv"
OUTPUT_DIR    = SANDBOX_ROOT / "tier1_step2c_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Configuration ----------------------------------------------------------
FEATURE_PAIR    = "Asc_x_MO"   # Calibration first; change to Asc_x_SU after
SMOOTH_WINDOWS  = [3, 5]       # Both Paper 1 scales; stability cross-check
# Arbitrary descriptive threshold for tallying high-gradient degrees.
# Exploratory only — no inferential weight.
RATE_GRAD_DESC_THRESHOLD = 0.001

# --- Sanity -----------------------------------------------------------------
for p in [SENTINEL, PER_EVENT_DIR, STRATUM_PATH, HOLDOUT_PATH, LABELS_PATH]:
    assert p.exists(), f"Required path not found: {p}"

# --- Engine-protocol helpers ------------------------------------------------
def circular_smooth(arr, window):
    """Engine-protocol circular smoothing: triple, centered rolling mean,
    middle third. Matches cell_v2_batch_v2_0_2 / HANDOFF_Workflow."""
    s = pd.Series(np.concatenate([arr, arr, arr]))
    sm = s.rolling(window=window, center=True, min_periods=window).mean()
    return sm.iloc[360:720].values

def per_degree_arrays(degrees, target):
    """Returns raw_rate[360], raw_count[360]."""
    deg = (np.asarray(degrees) % 360).astype(int)
    tgt = np.asarray(target).astype(int)
    sums   = np.bincount(deg, weights=tgt, minlength=360)
    counts = np.bincount(deg, minlength=360).astype(float)
    raw_rate = np.where(counts > 0, sums / counts, 0.0)
    return raw_rate, counts

def local_gradient(curve):
    """Central finite difference, wrap-aware."""
    n = len(curve)
    return np.array([(curve[(d+1) % n] - curve[(d-1) % n]) / 2.0 for d in range(n)])

# --- Load manifests ---------------------------------------------------------
strat   = pd.read_csv(STRATUM_PATH)
labels  = pd.read_csv(LABELS_PATH)
holdout = pd.read_csv(HOLDOUT_PATH)
explor_dates = set(holdout.loc[holdout["partition"] == "exploratory", "game_date"])
print(f"Exploratory partition: {len(explor_dates):,} game-dates.")

labels["is_HS"]  = (labels["total_runs_class"]      == "HS" ).astype(int)
labels["is_LS"]  = (labels["total_runs_class"]      == "LS" ).astype(int)
labels["is_BHW"] = (labels["margin_polarity_class"] == "BHW").astype(int)
labels["is_GHL"] = (labels["margin_polarity_class"] == "GHL").astype(int)

# --- Locate frame files -----------------------------------------------------
candidates = sorted(PER_EVENT_DIR.glob(f"{FEATURE_PAIR}_*.csv"))
print(f"\n{len(candidates)} per-event files for {FEATURE_PAIR}:")
for c in candidates: print(f"  {c.name}")
assert candidates, f"No per-event files found for {FEATURE_PAIR}."

# --- Configuration ----------------------------------------------------------
STRATA_FILTERS = {
    "all_explor":     lambda df: df,
    "regular_season": lambda df: df[df["stratum"] == "regular_season"],
    "post_season":    lambda df: df[df["stratum"] == "post_season"],
}
OUTCOME_CLASSES = ["HS", "LS", "BHW", "GHL"]

# --- Main loop --------------------------------------------------------------
curve_rows = []
summary_rows = []

for fpath in candidates:
    frame = fpath.stem.replace(f"{FEATURE_PAIR}_", "")
    print(f"\n--- Processing frame: {frame} ---")
    df = pd.read_csv(fpath, usecols=["event_id", "date", "raw_degree"])
    try:
        df["date"] = pd.to_datetime(df["date"], errors="coerce", format="mixed")
    except (TypeError, ValueError):
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["date_iso"] = df["date"].dt.strftime("%Y-%m-%d")
    df = df[df["date_iso"].isin(explor_dates)].copy()
    df = df.merge(strat, on="event_id").merge(labels, on="event_id")
    print(f"  Exploratory events: {len(df):,}")

    for stratum_name, sfilter in STRATA_FILTERS.items():
        d_s = sfilter(df)
        if len(d_s) == 0: continue
        for cls in OUTCOME_CLASSES:
            col = f"is_{cls}"
            n_class = int(d_s[col].sum())
            baseline = float(d_s[col].mean())
            raw_rate, raw_count = per_degree_arrays(
                d_s["raw_degree"].to_numpy(), d_s[col].to_numpy())

            for window in SMOOTH_WINDOWS:
                sm_rate  = circular_smooth(raw_rate,  window)
                sm_count = circular_smooth(raw_count, window)
                sm_lift  = sm_rate / baseline if baseline > 0 else np.zeros_like(sm_rate)
                rate_grad = local_gradient(sm_rate)
                lift_grad = local_gradient(sm_lift)

                for d in range(360):
                    curve_rows.append({
                        "frame": frame, "stratum": stratum_name, "class": cls,
                        "smooth_window": window, "degree": d,
                        "raw_rate": raw_rate[d], "raw_count": int(raw_count[d]),
                        "smoothed_rate":  sm_rate[d],
                        "smoothed_count": sm_count[d],
                        "smoothed_lift":  sm_lift[d],
                        "rate_gradient":  rate_grad[d],   # PRIMARY
                        "lift_gradient":  lift_grad[d],   # SECONDARY (= rate_grad / baseline)
                    })

                peak_rate_i = int(np.nanargmax(sm_rate))
                grad_i      = int(np.nanargmax(np.abs(rate_grad)))
                lift_grad_i = int(np.nanargmax(np.abs(lift_grad)))  # same idx by construction
                summary_rows.append({
                    "frame": frame, "stratum": stratum_name, "class": cls,
                    "smooth_window": window,
                    "n_stratum": len(d_s),
                    "n_class_in_stratum": n_class,
                    "baseline_rate": baseline,
                    "peak_smoothed_rate": float(sm_rate[peak_rate_i]),
                    "peak_lift": float(sm_lift[peak_rate_i]),
                    "peak_degree": peak_rate_i,
                    "peak_smoothed_count": float(sm_count[peak_rate_i]),
                    # PRIMARY: rate gradient
                    "max_abs_rate_gradient":     float(np.abs(rate_grad[grad_i])),
                    "max_rate_gradient_degree":  grad_i,
                    "mean_abs_rate_gradient":    float(np.nanmean(np.abs(rate_grad))),
                    "frac_above_rate_grad_thr":  float((np.abs(rate_grad) > RATE_GRAD_DESC_THRESHOLD).mean()),
                    # SECONDARY: lift gradient (= rate gradient / baseline)
                    "max_abs_lift_gradient":     float(np.abs(lift_grad[lift_grad_i])),
                })

# --- Write artifacts --------------------------------------------------------
curves_df  = pd.DataFrame(curve_rows)
summary_df = pd.DataFrame(summary_rows)
curves_path  = OUTPUT_DIR / f"step2c_per_degree_curves_{FEATURE_PAIR}.csv"
summary_path = OUTPUT_DIR / f"step2c_headline_summary_{FEATURE_PAIR}.csv"
curves_df.to_csv(curves_path, index=False)
summary_df.to_csv(summary_path, index=False)
print(f"\nWritten per-degree curves: {curves_path}")
print(f"Written headline summary:  {summary_path}")

# --- Console: all_explor rows only (24 rows: 4 classes × 3 frames × 2 windows)
print("\n=== Step 2c headline summary (all_explor only; full table in CSV) ===")
display_cols = ["frame", "class", "smooth_window", "n_class_in_stratum",
                "baseline_rate",
                "peak_smoothed_rate", "peak_lift", "peak_degree",
                "peak_smoothed_count",
                "max_abs_rate_gradient", "max_rate_gradient_degree",
                "mean_abs_rate_gradient", "frac_above_rate_grad_thr",
                "max_abs_lift_gradient"]
ae = summary_df[summary_df["stratum"] == "all_explor"].sort_values(
    ["class", "frame", "smooth_window"])
with pd.option_context("display.max_rows", None, "display.width", 220,
                       "display.float_format", "{:.4f}".format):
    print(ae[display_cols].to_string(index=False))

# --- Hash --------------------------------------------------------------------
with open(summary_path, "rb") as f:
    sha256 = hashlib.sha256(f.read()).hexdigest()
print(f"\nHeadline summary SHA256:\n{sha256}")

# --- Polar plot: lift curves (5° smoothing), all_explor, HS+LS and BHW+GHL --
PLOT_WINDOW = 5
ae_lifts = curves_df.loc[
    (curves_df["stratum"] == "all_explor") &
    (curves_df["smooth_window"] == PLOT_WINDOW), "smoothed_lift"].values
lift_max = float(np.nanmax(ae_lifts)) * 1.05

fig, axes = plt.subplots(2, len(candidates), figsize=(5*len(candidates), 10),
                         subplot_kw=dict(projection="polar"))
if len(candidates) == 1: axes = axes.reshape(2, 1)
theta = np.deg2rad(np.arange(360))

PAIRS = [("HS", "LS"), ("BHW", "GHL")]
for row_i, (cls_a, cls_b) in enumerate(PAIRS):
    for col_i, fpath in enumerate(candidates):
        frame = fpath.stem.replace(f"{FEATURE_PAIR}_", "")
        ax = axes[row_i, col_i]
        ax.plot(np.deg2rad(np.arange(361)), np.ones(361),
                color="black", linewidth=0.6, linestyle="--", alpha=0.5)
        for cls, color in [(cls_a, "#d62728"), (cls_b, "#1f77b4")]:
            sub = curves_df[(curves_df["frame"] == frame) &
                            (curves_df["stratum"] == "all_explor") &
                            (curves_df["class"] == cls) &
                            (curves_df["smooth_window"] == PLOT_WINDOW)].sort_values("degree")
            if len(sub) == 0: continue
            ax.plot(theta, sub["smoothed_lift"].values,
                    linewidth=1.4, label=cls, color=color)
        ax.set_ylim(0, lift_max)
        ax.set_title(f"{FEATURE_PAIR.replace('_',' ')}  {frame}  {cls_a} vs {cls_b}  "
                     f"(window={PLOT_WINDOW}°)", fontsize=10)
        ax.set_xticks(np.deg2rad([0, 90, 180, 270]))
        ax.set_xticklabels(["0°", "90°", "180°", "270°"])
        ax.set_yticklabels([])
        ax.legend(loc="upper right", bbox_to_anchor=(1.22, 1.10), fontsize=8)

plt.tight_layout()
lift_fig = OUTPUT_DIR / f"step2c_polar_lift_{FEATURE_PAIR}.png"
plt.savefig(lift_fig, dpi=140, bbox_inches="tight")
plt.show()
print(f"Polar lift plot: {lift_fig}")

# --- Linear plot: |dRate/dθ| (primary), per frame, all classes overlaid ----
fig, axes = plt.subplots(len(candidates), 1, figsize=(12, 3*len(candidates)),
                         sharex=True)
if len(candidates) == 1: axes = [axes]
for ax, fpath in zip(axes, candidates):
    frame = fpath.stem.replace(f"{FEATURE_PAIR}_", "")
    for cls, color in zip(OUTCOME_CLASSES,
                          ["#d62728", "#1f77b4", "#ff7f0e", "#2ca02c"]):
        sub = curves_df[(curves_df["frame"] == frame) &
                        (curves_df["stratum"] == "all_explor") &
                        (curves_df["class"] == cls) &
                        (curves_df["smooth_window"] == PLOT_WINDOW)].sort_values("degree")
        ax.plot(sub["degree"], np.abs(sub["rate_gradient"]),
                linewidth=1.0, label=cls, color=color)
    ax.axhline(RATE_GRAD_DESC_THRESHOLD, linestyle="--", linewidth=0.6,
               color="gray", label=f"descriptive thr = {RATE_GRAD_DESC_THRESHOLD}")
    ax.set_title(f"{FEATURE_PAIR.replace('_',' ')}  {frame}  "
                 f"|dRate/dθ|  (window={PLOT_WINDOW}°, all_explor)", fontsize=10)
    ax.set_ylabel("|dRate/dθ|")
    ax.legend(fontsize=8, loc="upper right")
axes[-1].set_xlabel("Degree")
plt.tight_layout()
grad_fig = OUTPUT_DIR / f"step2c_rate_gradient_{FEATURE_PAIR}.png"
plt.savefig(grad_fig, dpi=140, bbox_inches="tight")
plt.show()
print(f"Rate gradient plot: {grad_fig}")

print("\n=== Tier 1 Step 2c v2 complete ===")
