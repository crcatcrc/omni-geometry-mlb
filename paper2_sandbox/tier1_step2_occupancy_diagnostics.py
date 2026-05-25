"""
OMNI Paper 2 Sandbox — Tier 1 Step 2: per-frame occupancy diagnostics.

For the canonical Asc × MO feature pair, computes per-degree support
distributions (raw_degree occupancy histograms) separately within the
regular-season and post-season strata, for each available coordinate
frame (G-AZ priority; G-LON and G-RA as control frames).

For each (frame × stratum) cell:
  - 360-degree support histogram
  - smallest-arc-95 width (smallest contiguous arc containing 95% of events)
  - smallest-arc-99 width
  - coverage diagnostics (unique degrees occupied, empty degrees, per-degree
    mean / median / max / min)

The PS G-AZ arc width is compared against Paper 1's Asc (74°) and EA (45°)
bounded-G-AZ-origin reference arcs from Charter §4.3 — the mechanism that
makes G-AZ the most sensitive and most artifact-prone frame for Vector E.

All analysis is restricted to the exploratory partition (Charter §3 sealing).
Per Charter §1, output is treated as architecture-discovery signal, not
inferential evidence. Per §4.3, the four Vector E confounds remain active.

Tier 1 Step 2 artifact per Charter §4.1.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

SANDBOX_ROOT = Path("/content/drive/MyDrive/OMNI_PROJECT/paper2_sandbox")
GATE_DIR = SANDBOX_ROOT / "CONFIRMATORY_GATE"
SENTINEL = GATE_DIR / "sandbox_seal_v1_0.lock"

PER_EVENT_DIR = Path("/content/drive/MyDrive/OMNI_PROJECT/workspace/per_event_features")
STRATUM_PATH = SANDBOX_ROOT / "event_stratum_manifest_v1_0.csv"
HOLDOUT_PATH = SANDBOX_ROOT / "holdout_manifest_v1_0.csv"

OUTPUT_DIR = SANDBOX_ROOT / "tier1_step2_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Sanity ------------------------------------------------------------------
assert SENTINEL.exists(), f"Sentinel not found: {SENTINEL}"
assert PER_EVENT_DIR.exists(), f"Per-event directory not found: {PER_EVENT_DIR}"
assert STRATUM_PATH.exists(), f"Stratum manifest not found: {STRATUM_PATH}"
assert HOLDOUT_PATH.exists(), f"Holdout manifest not found: {HOLDOUT_PATH}"

# --- Locate frame files for Asc x MO ----------------------------------------
FEATURE_PAIR = "Asc_x_MO"
candidates = sorted(PER_EVENT_DIR.glob(f"{FEATURE_PAIR}_*.csv"))
print(f"Found {len(candidates)} per-event files matching {FEATURE_PAIR}_*.csv:")
for c in candidates:
    print(f"  {c.name}")
if len(candidates) == 0:
    raise FileNotFoundError(
        f"No per-event files found for {FEATURE_PAIR}. "
        f"Check {PER_EVENT_DIR} and confirm naming convention."
    )

def frame_from_filename(p):
    return p.stem.replace(f"{FEATURE_PAIR}_", "")

# --- Load manifests ----------------------------------------------------------
strat = pd.read_csv(STRATUM_PATH)
holdout = pd.read_csv(HOLDOUT_PATH)
explor_dates = set(holdout.loc[holdout["partition"] == "exploratory", "game_date"])
print(f"\nExploratory partition: {len(explor_dates):,} game-dates.")

# --- Helpers ----------------------------------------------------------------
def smallest_arc_containing(degrees, fraction=0.95):
    """Smallest contiguous circular arc containing `fraction` of points.
    Returns (arc_width_degrees, arc_start, arc_end). Handles wrap via doubling."""
    if len(degrees) == 0:
        return (np.nan, np.nan, np.nan)
    n = len(degrees)
    n_target = int(np.ceil(fraction * n))
    if n_target < 1:
        n_target = 1
    sorted_deg = np.sort(np.asarray(degrees) % 360).astype(float)
    doubled = np.concatenate([sorted_deg, sorted_deg + 360.0])
    best_width = 360.0
    best_start = 0.0
    for i in range(n):
        j = i + n_target - 1
        width = doubled[j] - doubled[i]
        if width < best_width:
            best_width = width
            best_start = sorted_deg[i]
    return (best_width, best_start, (best_start + best_width) % 360)

def circular_smooth(arr, window=5):
    """Engine-protocol circular smoothing: triple, centered rolling mean, return middle third."""
    s = pd.Series(np.concatenate([arr, arr, arr]))
    sm = s.rolling(window=window, center=True, min_periods=window).mean()
    return sm.iloc[360:720].values

def coverage_audit(degrees):
    """Per-degree support counts (0-359) and summary statistics."""
    if len(degrees) == 0:
        return None
    deg = (np.asarray(degrees) % 360).astype(int)
    bins = np.bincount(deg, minlength=360)
    return {
        "n_events": int(len(deg)),
        "n_unique_degrees": int((bins > 0).sum()),
        "n_empty_degrees": int((bins == 0).sum()),
        "mean_per_degree": float(bins.mean()),
        "median_per_degree": float(np.median(bins)),
        "max_per_degree": int(bins.max()),
        "min_per_degree": int(bins.min()),
        "support_arc_95": smallest_arc_containing(deg, 0.95),
        "support_arc_99": smallest_arc_containing(deg, 0.99),
        "bins": bins,
    }

# --- Paper 1 reference arcs (Charter §4.3 mechanism reference) --------------
PAPER1_REFS = {
    "Asc bounded G-AZ origin (Paper 1)": 74,
    "EA bounded G-AZ origin (Paper 1)":  45,
}

# --- Per-frame loop ---------------------------------------------------------
results = {}
for fpath in candidates:
    frame = frame_from_filename(fpath)
    print(f"\n=== {FEATURE_PAIR.replace('_', ' ')}  frame={frame} ===")

    df = pd.read_csv(fpath, usecols=["event_id", "date", "raw_degree"])
    # Engine-protocol date parsing
    try:
        df["date"] = pd.to_datetime(df["date"], errors="coerce", format="mixed")
    except (TypeError, ValueError):
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    df = df.merge(strat, on="event_id", how="left")
    df["date_iso"] = df["date"].dt.strftime("%Y-%m-%d")

    # Restrict to exploratory partition only
    n_before = len(df)
    df = df[df["date_iso"].isin(explor_dates)].copy()
    n_after = len(df)
    print(f"  Events: {n_before:,} total → {n_after:,} in exploratory partition")

    rs_audit = coverage_audit(df.loc[df["stratum"] == "regular_season", "raw_degree"])
    ps_audit = coverage_audit(df.loc[df["stratum"] == "post_season", "raw_degree"])

    print(f"  RS: n={rs_audit['n_events']:,}  unique_degs={rs_audit['n_unique_degrees']:>3d}/360  "
          f"empty={rs_audit['n_empty_degrees']:>3d}")
    print(f"  PS: n={ps_audit['n_events']:,}  unique_degs={ps_audit['n_unique_degrees']:>3d}/360  "
          f"empty={ps_audit['n_empty_degrees']:>3d}")

    rs_a95, rs_s95, rs_e95 = rs_audit["support_arc_95"]
    ps_a95, ps_s95, ps_e95 = ps_audit["support_arc_95"]
    rs_a99, _, _ = rs_audit["support_arc_99"]
    ps_a99, _, _ = ps_audit["support_arc_99"]
    print(f"  RS 95% support arc: {rs_a95:>6.1f}°   (start={rs_s95:>5.1f}°  end={rs_e95:>5.1f}°)")
    print(f"  PS 95% support arc: {ps_a95:>6.1f}°   (start={ps_s95:>5.1f}°  end={ps_e95:>5.1f}°)")
    print(f"  RS 99% support arc: {rs_a99:>6.1f}°")
    print(f"  PS 99% support arc: {ps_a99:>6.1f}°")
    compression_ratio = ps_a95 / rs_a95 if rs_a95 > 0 else np.nan
    print(f"  PS/RS 95%-arc compression ratio: {compression_ratio:.3f}")

    if frame.replace("_", "-").upper() in ("G-AZ", "GAZ"):
        print(f"\n  *** Paper 1 concentration-regime reference comparison (G-AZ frame) ***")
        for label, ref in PAPER1_REFS.items():
            print(f"    {label}: {ref}°")
        print(f"    Asc × MO PS G-AZ 95% support arc: {ps_a95:.1f}°")
        if ps_a95 <= 90:
            print(f"    NOTE: PS G-AZ 95% arc is narrow (<= 90°). Concentration-regime "
                  f"mechanism is operationally visible. Charter §4.3 confounds remain active.")

    results[frame] = {"rs": rs_audit, "ps": ps_audit}

# --- Per-frame summary table ------------------------------------------------
rows = []
for frame, r in results.items():
    rows.append({
        "frame": frame,
        "n_rs": r["rs"]["n_events"],
        "n_ps": r["ps"]["n_events"],
        "rs_unique_degs": r["rs"]["n_unique_degrees"],
        "ps_unique_degs": r["ps"]["n_unique_degrees"],
        "rs_arc95_deg": r["rs"]["support_arc_95"][0],
        "ps_arc95_deg": r["ps"]["support_arc_95"][0],
        "rs_arc99_deg": r["rs"]["support_arc_99"][0],
        "ps_arc99_deg": r["ps"]["support_arc_99"][0],
        "ps_over_rs_arc95": (r["ps"]["support_arc_95"][0] / r["rs"]["support_arc_95"][0]
                             if r["rs"]["support_arc_95"][0] > 0 else np.nan),
    })
summary = pd.DataFrame(rows)
print("\n=== Per-frame summary ===")
print(summary.to_string(index=False))

# --- Save artifacts ---------------------------------------------------------
summary_path = OUTPUT_DIR / f"step2_per_frame_summary_{FEATURE_PAIR}.csv"
summary.to_csv(summary_path, index=False)
print(f"\nSummary written: {summary_path}")

for frame, r in results.items():
    hist = pd.DataFrame({
        "degree":    np.arange(360),
        "rs_count":  r["rs"]["bins"],
        "ps_count":  r["ps"]["bins"],
        "rs_rate":   r["rs"]["bins"] / max(r["rs"]["n_events"], 1),
        "ps_rate":   r["ps"]["bins"] / max(r["ps"]["n_events"], 1),
    })
    out = OUTPUT_DIR / f"step2_histogram_{FEATURE_PAIR}_{frame}.csv"
    hist.to_csv(out, index=False)
print(f"Per-frame histograms written to {OUTPUT_DIR}/")

# --- Polar visualisation ----------------------------------------------------
n_frames = len(results)
fig, axes = plt.subplots(1, n_frames, figsize=(5 * n_frames, 5),
                         subplot_kw=dict(projection="polar"))
if n_frames == 1:
    axes = [axes]
theta = np.deg2rad(np.arange(360))

for ax, (frame, r) in zip(axes, results.items()):
    rs_rate_sm = circular_smooth(r["rs"]["bins"] / max(r["rs"]["n_events"], 1), window=5)
    ps_rate_sm = circular_smooth(r["ps"]["bins"] / max(r["ps"]["n_events"], 1), window=5)
    ax.plot(theta, rs_rate_sm, linewidth=1.2, label=f"RS (n={r['rs']['n_events']:,})", color="#1f77b4")
    ax.plot(theta, ps_rate_sm, linewidth=1.2, label=f"PS (n={r['ps']['n_events']:,})", color="#d62728")
    ax.set_title(f"{FEATURE_PAIR.replace('_',' ')}  {frame}", fontsize=11)
    ax.set_xticks(np.deg2rad([0, 90, 180, 270]))
    ax.set_xticklabels(["0°", "90°", "180°", "270°"])
    ax.set_yticklabels([])
    ax.legend(loc="upper right", bbox_to_anchor=(1.20, 1.10), fontsize=8)
plt.tight_layout()
fig_path = OUTPUT_DIR / f"step2_polar_occupancy_{FEATURE_PAIR}.png"
plt.savefig(fig_path, dpi=140, bbox_inches="tight")
plt.show()
print(f"Polar plot: {fig_path}")

print("\n=== Tier 1 Step 2 occupancy diagnostics complete ===")
