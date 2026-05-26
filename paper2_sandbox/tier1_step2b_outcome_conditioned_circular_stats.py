"""
OMNI Paper 2 Sandbox — Tier 1 Step 2b: outcome-conditioned circular statistics.

Primary research question (PI framing, ChatG-reviewed):
Within each stratum and coordinate frame, do outcome-conditioned circular
distributions diverge in structured ways? The OMNI null is

    H0: HS and LS (or BHW and GHL) share the same circular distribution
        within a given feature / frame / stratum.

RS vs PS comparison is treated as a modifier of these primary contrasts,
not as the primary question.

Per Charter §4.3 sample-asymmetry mandate, bootstrap confidence intervals
on effect size are included from the start (PS-cell n ≈ 100 per class for
BHW vs GHL; ≈ 50 per class for HS vs LS — both at or near the floor where
asymptotic-only inference is unsafe).

Per Charter §1, all output is treated as architecture-discovery signal,
not inferential evidence. Significance values are diagnostic.

Tier 1 Step 2b artifact per Charter §4.1.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chi2 as chi2dist

# --- Paths ------------------------------------------------------------------
SANDBOX_ROOT = Path("/content/drive/MyDrive/OMNI_PROJECT/paper2_sandbox")
GATE_DIR = SANDBOX_ROOT / "CONFIRMATORY_GATE"
SENTINEL = GATE_DIR / "sandbox_seal_v1_0.lock"
PER_EVENT_DIR = Path("/content/drive/MyDrive/OMNI_PROJECT/workspace/per_event_features")
STRATUM_PATH = SANDBOX_ROOT / "event_stratum_manifest_v1_0.csv"
HOLDOUT_PATH = SANDBOX_ROOT / "holdout_manifest_v1_0.csv"
LABELS_PATH = SANDBOX_ROOT / "outcome_labels_manifest_v1_0.csv"
OUTPUT_DIR = SANDBOX_ROOT / "tier1_step2_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Configuration ----------------------------------------------------------
FEATURE_PAIR = "Asc_x_MO"
N_BINS = 36           # 10°-wide bins for chi-square
N_PERMS = 2000        # permutation iterations
N_BOOT = 2000         # bootstrap iterations
RNG_SEED = 20260524   # match OMNI_P2_SEED
SIG_LEVEL = 0.05
EFFECT_FLOOR = 0.10   # Cramer's V flagged at >= this value

# --- Sanity -----------------------------------------------------------------
for p in [SENTINEL, PER_EVENT_DIR, STRATUM_PATH, HOLDOUT_PATH, LABELS_PATH]:
    assert p.exists(), f"Required path not found: {p}"

# --- Circular-statistics helpers --------------------------------------------
def circular_mean(deg):
    if len(deg) == 0: return np.nan
    th = np.deg2rad(deg)
    return float(np.rad2deg(np.arctan2(np.sin(th).mean(), np.cos(th).mean())) % 360)

def mean_resultant_length(deg):
    if len(deg) == 0: return np.nan
    th = np.deg2rad(deg)
    return float(np.hypot(np.cos(th).mean(), np.sin(th).mean()))

def axial_resultant_length(deg):
    """R̄ on 2θ — captures bilateral / axial concentration."""
    return mean_resultant_length(2 * np.asarray(deg))

def rayleigh_p(deg):
    """Approximate Rayleigh test for non-uniformity (good for n ≥ 10)."""
    n = len(deg)
    if n < 2: return np.nan
    R = mean_resultant_length(deg)
    z = n * R**2
    return float(np.exp(-z) * (1 + (2*z - z**2) / (4*n)))

def peak_degree_smoothed(deg, n_bins=72, window=5):
    """Peak of 5°-binned, circularly smoothed density."""
    if len(deg) == 0: return np.nan
    bins = np.linspace(0, 360, n_bins + 1)
    h, _ = np.histogram(np.asarray(deg) % 360, bins=bins)
    # Circular smooth (engine protocol: triple + centered rolling mean)
    s = pd.Series(np.concatenate([h, h, h])).rolling(
        window=window, center=True, min_periods=window).mean()
    smoothed = s.iloc[n_bins:2*n_bins].values
    return float((np.argmax(smoothed) + 0.5) * (360 / n_bins))

def chi2_two_sample(d1, d2, n_bins=N_BINS):
    """Chi-square two-sample on binned circular data. Returns (chi2, df, p_asym, cramers_v)."""
    bins = np.linspace(0, 360, n_bins + 1)
    h1, _ = np.histogram(np.asarray(d1) % 360, bins=bins)
    h2, _ = np.histogram(np.asarray(d2) % 360, bins=bins)
    n1, n2 = int(h1.sum()), int(h2.sum())
    if n1 == 0 or n2 == 0:
        return (np.nan, 0, np.nan, np.nan)
    n_tot = n1 + n2
    pooled = h1 + h2
    e1 = pooled * n1 / n_tot
    e2 = pooled * n2 / n_tot
    mask = (e1 > 0) & (e2 > 0)
    chi2 = float(((h1[mask] - e1[mask])**2 / e1[mask]
                + (h2[mask] - e2[mask])**2 / e2[mask]).sum())
    df = int(mask.sum() - 1)
    p_asym = float(1 - chi2dist.cdf(chi2, df)) if df > 0 else np.nan
    cv = float(np.sqrt(chi2 / n_tot)) if n_tot > 0 else np.nan
    return (chi2, df, p_asym, cv)

def permutation_p(d1, d2, n_perms=N_PERMS, n_bins=N_BINS, rng=None):
    """Permutation p-value for chi-square two-sample."""
    if rng is None:
        rng = np.random.default_rng(RNG_SEED)
    d1 = np.asarray(d1); d2 = np.asarray(d2)
    obs, _, _, _ = chi2_two_sample(d1, d2, n_bins=n_bins)
    if np.isnan(obs):
        return np.nan
    pooled = np.concatenate([d1, d2])
    n1 = len(d1)
    n_extreme = 0
    for _ in range(n_perms):
        idx = rng.permutation(len(pooled))
        s1 = pooled[idx[:n1]]
        s2 = pooled[idx[n1:]]
        c, _, _, _ = chi2_two_sample(s1, s2, n_bins=n_bins)
        if c >= obs:
            n_extreme += 1
    return (n_extreme + 1) / (n_perms + 1)

def bootstrap_cramers_v_ci(d1, d2, n_boot=N_BOOT, n_bins=N_BINS, ci=0.95, rng=None):
    """Bootstrap CI for Cramer's V."""
    if rng is None:
        rng = np.random.default_rng(RNG_SEED + 1)
    d1 = np.asarray(d1); d2 = np.asarray(d2)
    n1, n2 = len(d1), len(d2)
    if n1 == 0 or n2 == 0:
        return (np.nan, np.nan)
    cvs = np.empty(n_boot)
    for i in range(n_boot):
        s1 = d1[rng.integers(0, n1, n1)]
        s2 = d2[rng.integers(0, n2, n2)]
        _, _, _, cv = chi2_two_sample(s1, s2, n_bins=n_bins)
        cvs[i] = cv
    alpha = (1 - ci) / 2
    return (float(np.nanquantile(cvs, alpha)), float(np.nanquantile(cvs, 1 - alpha)))

# --- Load manifests ---------------------------------------------------------
strat = pd.read_csv(STRATUM_PATH)
labels = pd.read_csv(LABELS_PATH)
holdout = pd.read_csv(HOLDOUT_PATH)
explor_dates = set(holdout.loc[holdout["partition"] == "exploratory", "game_date"])
print(f"Exploratory partition: {len(explor_dates):,} game-dates.")

# --- Locate frame files for the feature pair --------------------------------
candidates = sorted(PER_EVENT_DIR.glob(f"{FEATURE_PAIR}_*.csv"))
print(f"\n{len(candidates)} per-event files for {FEATURE_PAIR}:")
for c in candidates: print(f"  {c.name}")
if not candidates:
    raise FileNotFoundError(f"No per-event files found for {FEATURE_PAIR}.")

# --- Contrast grid (PI/ChatG-specified primary set) -------------------------
STRATA_FILTERS = {
    "all_explor":     lambda df: df,
    "regular_season": lambda df: df[df["stratum"] == "regular_season"],
    "post_season":    lambda df: df[df["stratum"] == "post_season"],
}
CONTRASTS = [
    {"family": "total_runs",       "class_a": "HS",  "class_b": "LS"},
    {"family": "margin_polarity",  "class_a": "BHW", "class_b": "GHL"},
]
class_col = {"total_runs": "total_runs_class", "margin_polarity": "margin_polarity_class"}

# --- Per-frame, per-contrast loop -------------------------------------------
rng_perm = np.random.default_rng(RNG_SEED)
rng_boot = np.random.default_rng(RNG_SEED + 1)
results = []

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

    for stratum_name, sfilter in STRATA_FILTERS.items():
        d_s = sfilter(df)
        for ct in CONTRASTS:
            col = class_col[ct["family"]]
            a = d_s.loc[d_s[col] == ct["class_a"], "raw_degree"].to_numpy()
            b = d_s.loc[d_s[col] == ct["class_b"], "raw_degree"].to_numpy()
            chi2, dfree, p_asym, cv = chi2_two_sample(a, b)
            p_perm = permutation_p(a, b, rng=rng_perm)
            ci_lo, ci_hi = bootstrap_cramers_v_ci(a, b, rng=rng_boot)
            results.append({
                "frame":       frame,
                "stratum":     stratum_name,
                "family":      ct["family"],
                "contrast":    f"{ct['class_a']}_vs_{ct['class_b']}",
                "n_a":         len(a), "n_b": len(b),
                "mean_a":      circular_mean(a),
                "mean_b":      circular_mean(b),
                "Rbar_a":      mean_resultant_length(a),
                "Rbar_b":      mean_resultant_length(b),
                "axRbar_a":    axial_resultant_length(a),
                "axRbar_b":    axial_resultant_length(b),
                "peak_a":      peak_degree_smoothed(a),
                "peak_b":      peak_degree_smoothed(b),
                "rayleigh_p_a": rayleigh_p(a),
                "rayleigh_p_b": rayleigh_p(b),
                "chi2":        chi2,
                "df":          dfree,
                "p_chi2_asym": p_asym,
                "p_chi2_perm": p_perm,
                "cramers_v":   cv,
                "cv_ci_lo":    ci_lo,
                "cv_ci_hi":    ci_hi,
            })

# --- Output table -----------------------------------------------------------
summary = pd.DataFrame(results)
sort_cols = ["family", "frame", "stratum"]
summary_sorted = summary.sort_values(["cramers_v"], ascending=False).reset_index(drop=True)

# Concise console view
display_cols = ["frame", "stratum", "contrast", "n_a", "n_b",
                "Rbar_a", "Rbar_b", "axRbar_a", "axRbar_b",
                "peak_a", "peak_b",
                "p_chi2_perm", "cramers_v", "cv_ci_lo", "cv_ci_hi"]
print("\n=== Outcome-conditioned circular statistics — sorted by Cramer's V ===")
with pd.option_context("display.max_rows", None, "display.width", 200,
                       "display.float_format", "{:.3f}".format):
    print(summary_sorted[display_cols].to_string(index=False))

# Flagged rows: significant + meaningful effect
flagged = summary_sorted[
    (summary_sorted["p_chi2_perm"] < SIG_LEVEL) &
    (summary_sorted["cramers_v"] >= EFFECT_FLOOR)
]
print(f"\nRows passing diagnostic threshold (p_perm < {SIG_LEVEL} AND Cramer's V >= {EFFECT_FLOOR}):")
if len(flagged) > 0:
    with pd.option_context("display.max_rows", None, "display.width", 200,
                           "display.float_format", "{:.3f}".format):
        print(flagged[display_cols].to_string(index=False))
else:
    print("  (none — no contrast at this feature meets both criteria)")

# --- Write artifact ---------------------------------------------------------
out_path = OUTPUT_DIR / f"step2b_outcome_conditioned_circular_stats_{FEATURE_PAIR}.csv"
summary.to_csv(out_path, index=False)
print(f"\nWritten: {out_path}")

# --- Polar plots: HS vs LS and BHW vs GHL across frames (all_explor) --------
fig, axes = plt.subplots(2, len(candidates), figsize=(5*len(candidates), 10),
                         subplot_kw=dict(projection="polar"))
if len(candidates) == 1:
    axes = axes.reshape(2, 1)
theta = np.deg2rad(np.arange(360))

for col_i, fpath in enumerate(candidates):
    frame = fpath.stem.replace(f"{FEATURE_PAIR}_", "")
    df = pd.read_csv(fpath, usecols=["event_id", "date", "raw_degree"])
    try:
        df["date"] = pd.to_datetime(df["date"], errors="coerce", format="mixed")
    except (TypeError, ValueError):
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["date_iso"] = df["date"].dt.strftime("%Y-%m-%d")
    df = df[df["date_iso"].isin(explor_dates)].merge(labels, on="event_id")

    for row_i, ct in enumerate(CONTRASTS):
        col = class_col[ct["family"]]
        ax = axes[row_i, col_i]
        for cls, color in [(ct["class_a"], "#d62728"), (ct["class_b"], "#1f77b4")]:
            deg = df.loc[df[col] == cls, "raw_degree"].to_numpy()
            if len(deg) == 0: continue
            bins = np.bincount((deg % 360).astype(int), minlength=360)
            rate = bins / max(bins.sum(), 1)
            # Smooth (engine protocol)
            s = pd.Series(np.concatenate([rate, rate, rate])).rolling(
                window=11, center=True, min_periods=11).mean()
            sm = s.iloc[360:720].values
            ax.plot(theta, sm, linewidth=1.3, label=f"{cls} (n={len(deg):,})", color=color)
        ax.set_title(f"{FEATURE_PAIR.replace('_',' ')}  {frame}  {ct['family']}", fontsize=10)
        ax.set_xticks(np.deg2rad([0, 90, 180, 270]))
        ax.set_xticklabels(["0°", "90°", "180°", "270°"])
        ax.set_yticklabels([])
        ax.legend(loc="upper right", bbox_to_anchor=(1.22, 1.10), fontsize=8)

plt.tight_layout()
fig_path = OUTPUT_DIR / f"step2b_polar_outcome_contrasts_{FEATURE_PAIR}.png"
plt.savefig(fig_path, dpi=140, bbox_inches="tight")
plt.show()
print(f"Polar plot: {fig_path}")

print("\n=== Tier 1 Step 2b outcome-conditioned circular statistics complete ===")
