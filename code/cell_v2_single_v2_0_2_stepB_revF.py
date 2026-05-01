"""
================================================================================
OMNI PROJECT — PHASE A v2.0 PRODUCTION ENGINE
================================================================================

v2.0 = v1.5 (frozen, bit-identical Phase A) + Phase B (temporal validation)
     + per-event ML extraction layer + run manifest.

Per-feature, per-run outputs:
    * Phase A registry row    (locks + structural diagnostics; identical to v1.5)
    * Phase B registry row    (3-/5-/7-block persistence under locked params)
    * Per-event feature CSV   (raw degree, smoothed lift, distance-to-peak, etc.)
    * Diagnostic CSVs         (smoothed_360, lift_vs_N, window_diag — as in v1.5)

Aggregate (across runs):
    * omni_feature_registry.json/csv     — Phase A
    * temporal_persistence.csv           — Phase B
    * top_degrees_by_feature.json        — locked top-N degree sets per feature
    * /per_event_features/<feature>.csv  — ML-ready per-game columns
    * run_manifest.csv                   — provenance record per batch run

Phase A locks are guaranteed bit-identical to v1.5: window selection,
plateau detection, scale-structure annotation, and SHA-256 fingerprint logic
are unchanged. Phase B and per-event extraction are added strictly on top.

Schema version: 2.0
================================================================================
"""

from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


# ============================================================================
# CONFIGURATION — frozen from v1.5; do not modify without schema bump
# ============================================================================

ORB_WINDOWS: tuple[int, ...] = (3, 4, 5)
TOP_N_GRID: np.ndarray = np.arange(40, 201, 1)
MIN_SMOOTHED_COUNT_AT_PEAK: int = 30
LOCK_SATURATION_PCT: float = 98.0
ASYMPTOTE_DIAGNOSTIC_LOW: float = 95.0
ASYMPTOTE_DIAGNOSTIC_HIGH: float = 99.0
SCALE_FLAG_THRESHOLDS = {"scale_invariant": 5, "mild_multiscale": 15}

# Phase B — temporal validation (per Handoff 2)
TEMPORAL_SCHEMES: dict[str, list[tuple[str, int, int]]] = {
    "3_block": [
        ("2000-2007", 2000, 2007),
        ("2008-2015", 2008, 2015),
        ("2016-2024", 2016, 2024),
    ],
    "5_block": [
        ("2000-2004", 2000, 2004),
        ("2005-2009", 2005, 2009),
        ("2010-2014", 2010, 2014),
        ("2015-2019", 2015, 2019),
        ("2020-2024", 2020, 2024),
    ],
    "7_block": [
        ("2000-2003", 2000, 2003),
        ("2004-2006", 2004, 2006),
        ("2007-2009", 2007, 2009),
        ("2010-2012", 2010, 2012),
        ("2013-2015", 2013, 2015),
        ("2016-2018", 2016, 2018),
        ("2019-2024", 2019, 2024),
    ],
}

# Persistence thresholds — scheme-aware. A block is "persistent" if the
# anchor region (peak_degree +/- ANCHOR_HALF_WIDTH_DEG) shows MAX smoothed
# lift >= ANCHOR_LIFT_FLOOR. This is the PRIMARY persistence test.
#
# The field-based test (full locked top-N set) is retained as a SECONDARY
# diagnostic: it asks the dilute question "does the entire 98%-saturation
# region remain elevated?" rather than the focused question "does the peak
# region recur?" The classification flag uses anchor persistence only.
#
# v2.0.2 patch: anchor_max replaces anchor_mean as the primary statistic.
# The mean-based test was over-rejecting strong signals because neighborhood
# dips dragged the average below 1.15, even when the peak itself cleared
# the floor. Empirically verified on G-LON HS: 6/7 blocks have lift >= 1.15
# at the exact peak degree (220°), which the mean test obscured. Using max
# within the anchor region restores the correct test while preserving 1-2
# degrees of tolerance for smoothing/binning jitter.
ANCHOR_HALF_WIDTH_DEG: int = 10           # peak +/- this defines anchor region
ANCHOR_LIFT_FLOOR: float = 1.15           # max smoothed lift in anchor region

# Field (secondary, descriptive) thresholds: relaxed because the field test
# is operating on a diluted set; reported but does not drive classification.
FIELD_LIFT_FLOOR: float = 1.05
FIELD_BREADTH_FLOOR: float = 0.40

# Legacy constants retained for backward compatibility / references.
PERSISTENCE_LIFT_FLOOR: float = ANCHOR_LIFT_FLOOR
PERSISTENCE_BREADTH_FLOOR: float = FIELD_BREADTH_FLOOR
PERSISTENCE_MIN_BLOCKS: dict[str, int] = {"3_block": 2, "5_block": 3, "7_block": 3}
PERSISTENCE_ANCHOR_BLOCKS: dict[str, int] = {"3_block": 3, "5_block": 4, "7_block": 5}

DATE_COL = "Date"
RUNS_COL = "Total Runs Scored"
HIGH_THRESHOLD = 16
LOW_THRESHOLD = 3
SCHEMA_VERSION = "2.0.2"


# ============================================================================
# CORE NUMERICS — frozen from v1.5
# ============================================================================

def _circular_tile(values: np.ndarray) -> np.ndarray:
    return np.concatenate([values, values, values])


def circular_smooth_nan(values: np.ndarray, window: int) -> np.ndarray:
    s = pd.Series(_circular_tile(values)).rolling(
        window=window, center=True, min_periods=1
    ).mean()
    return s.iloc[360:720].to_numpy()


def circular_rolling_sum(values: np.ndarray, window: int) -> np.ndarray:
    s = pd.Series(_circular_tile(values)).rolling(
        window=window, center=True, min_periods=1
    ).sum()
    return s.iloc[360:720].to_numpy()


def circ_dist(a: int, b: int) -> int:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def build_degree_lift_table(df: pd.DataFrame, target_col: str, window: int) -> pd.DataFrame:
    baseline = df[target_col].mean()
    if baseline <= 0:
        raise ValueError(f"Baseline rate for {target_col} is non-positive.")
    g = (df.groupby("Degree")[target_col].agg(["mean", "count"])
           .rename(columns={"mean": "Rate", "count": "Count"}).reset_index())
    full = pd.DataFrame({"Degree": np.arange(360)}).merge(g, on="Degree", how="left")
    full["Count"] = full["Count"].fillna(0).astype(int)
    full["Lift"] = full["Rate"] / baseline
    full["Smoothed_Lift"] = circular_smooth_nan(full["Lift"].to_numpy(), window)
    full["Smoothed_Count"] = circular_rolling_sum(
        full["Count"].astype(float).to_numpy(), window
    )
    return full


# ============================================================================
# A1: WINDOW SELECTION — frozen from v1.5
# ============================================================================

def select_window(df: pd.DataFrame, target_col: str) -> tuple[int, list[dict]]:
    diags = []
    for w in ORB_WINDOWS:
        c = build_degree_lift_table(df, target_col, w)
        idx = int(c["Smoothed_Lift"].idxmax())
        diags.append({
            "window": w,
            "peak_degree": int(c.loc[idx, "Degree"]),
            "peak_smoothed_lift": float(c.loc[idx, "Smoothed_Lift"]),
            "smoothed_count_at_peak": float(c.loc[idx, "Smoothed_Count"]),
            "valid": bool(c.loc[idx, "Smoothed_Count"] >= MIN_SMOOTHED_COUNT_AT_PEAK),
        })
    valid = [d for d in diags if d["valid"]]
    pool = valid if valid else diags
    chosen = max(pool, key=lambda d: d["peak_smoothed_lift"])
    return chosen["window"], diags


# ============================================================================
# A2: SATURATION-BASED LOCK — frozen from v1.5
# ============================================================================

def lift_vs_n_curve(curve_360: pd.DataFrame) -> pd.DataFrame:
    lift = curve_360["Smoothed_Lift"].to_numpy()
    above1_total = np.nansum(np.clip(lift - 1.0, 0, None))
    if above1_total <= 0:
        raise ValueError("No above-baseline signal present.")
    sortable = np.where(np.isnan(lift), -np.inf, lift)
    sorted_lift = lift[np.argsort(-sortable)]
    rows = [{
        "N": int(n),
        "Pct_Above1_Signal": 100.0 * np.nansum(
            np.clip(sorted_lift[:n] - 1.0, 0, None)
        ) / above1_total,
    } for n in TOP_N_GRID]
    return pd.DataFrame(rows)


def smallest_n_at_threshold(curve: pd.DataFrame, threshold_pct: float) -> Optional[int]:
    arr = curve.set_index("N")["Pct_Above1_Signal"]
    crossings = arr[arr >= threshold_pct]
    return int(crossings.index.min()) if len(crossings) else None


def kneedle(curve: pd.DataFrame) -> Optional[int]:
    n = curve["N"].to_numpy(float)
    p = curve["Pct_Above1_Signal"].to_numpy(float)
    if len(n) < 3:
        return None
    nn = (n - n.min()) / (n.max() - n.min())
    pn = (p - p.min()) / (p.max() - p.min() + 1e-12)
    return int(n[int(np.argmax(pn - nn))])


def detect_plateau(curve: pd.DataFrame) -> dict:
    n_lock = smallest_n_at_threshold(curve, LOCK_SATURATION_PCT)
    return {
        "plateau_n_locked": n_lock,
        "lock_threshold_pct": LOCK_SATURATION_PCT,
        "lock_succeeded": n_lock is not None,
        "n_core_kneedle": kneedle(curve),
        "n_asymptote_95": smallest_n_at_threshold(curve, ASYMPTOTE_DIAGNOSTIC_LOW),
        "n_asymptote_99": smallest_n_at_threshold(curve, ASYMPTOTE_DIAGNOSTIC_HIGH),
        "max_capture_in_scan": float(curve["Pct_Above1_Signal"].max()),
        "curve": curve,
    }


def classify_scale_structure(drift: int) -> str:
    if drift <= SCALE_FLAG_THRESHOLDS["scale_invariant"]:
        return "scale_invariant"
    if drift <= SCALE_FLAG_THRESHOLDS["mild_multiscale"]:
        return "mild_multiscale"
    return "strong_multiscale"


def data_sha256(df: pd.DataFrame, feature_col: str) -> str:
    cols = [DATE_COL, RUNS_COL, feature_col, "High_Target", "Low_Target"]
    payload = pd.util.hash_pandas_object(df[cols], index=False).values.tobytes()
    return hashlib.sha256(payload).hexdigest()[:16]


# ============================================================================
# PHASE A — frozen v1.5
# ============================================================================

def phase_a_target(df: pd.DataFrame, feature_col: str, target: str
                   ) -> tuple[dict, dict, pd.DataFrame, list[dict]]:
    target_col = "High_Target" if target == "High" else "Low_Target"
    w, win_diag = select_window(df, target_col)
    c360 = build_degree_lift_table(df, target_col, w)
    pl = detect_plateau(lift_vs_n_curve(c360))
    idx = int(c360["Smoothed_Lift"].idxmax())

    peak_by_window = {d["window"]: d["peak_degree"] for d in win_diag}
    lift_by_window = {d["window"]: round(d["peak_smoothed_lift"], 4) for d in win_diag}
    peaks = list(peak_by_window.values())
    drift = max((circ_dist(a, b) for a in peaks for b in peaks), default=0) if len(peaks) > 1 else 0
    locked_peak = int(c360.loc[idx, "Degree"])
    peaks_within_5 = sum(1 for p in peaks if circ_dist(p, locked_peak) <= 5)
    flag = classify_scale_structure(drift)
    locked_peak_count = next(
        (d["smoothed_count_at_peak"] for d in win_diag if d["window"] == w), float("nan")
    )

    rec = {
        "feature": feature_col,
        "target": target,
        "window_locked": w,
        "n_locked": pl["plateau_n_locked"] if pl["lock_succeeded"] else -1,
        "lock_threshold_pct": pl["lock_threshold_pct"],
        "lock_succeeded": pl["lock_succeeded"],
        "max_capture_in_scan": pl["max_capture_in_scan"],
        "n_core_kneedle": pl["n_core_kneedle"],
        "n_asymptote_95": pl["n_asymptote_95"],
        "n_asymptote_99": pl["n_asymptote_99"],
        "peak_degree": locked_peak,
        "peak_smoothed_lift": float(c360.loc[idx, "Smoothed_Lift"]),
        "peak_smoothed_count": float(locked_peak_count),
        "peak_degree_by_window": json.dumps(peak_by_window),
        "peak_lift_by_window": json.dumps(lift_by_window),
        "window_drift_deg": int(drift),
        "peaks_within_5_of_lock": int(peaks_within_5),
        "scale_structure_flag": flag,
        "baseline_rate": float(df[target_col].mean()),
        "n_observations": int(len(df)),
        "data_sha256": data_sha256(df, feature_col),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "phase": "A",
        "schema_version": SCHEMA_VERSION,
    }
    return rec, pl, c360, win_diag


# ============================================================================
# PHASE B — temporal validation under locked Phase A parameters
# ============================================================================

def phase_b_target(df: pd.DataFrame, feature_col: str, target: str,
                   phase_a_rec: dict, phase_a_curve_360: pd.DataFrame
                   ) -> dict:
    """
    Test whether the structure detected globally by Phase A recurs across
    temporal partitions of the data.

    PRIMARY TEST (anchor-based, drives classification):
      For each block, compute the smoothed lift curve at the locked window,
      then take the MAX smoothed lift across the anchor region defined as
      peak_degree +/- ANCHOR_HALF_WIDTH_DEG. The block is persistent if that
      maximum meets ANCHOR_LIFT_FLOOR.

    SECONDARY TEST (field-based, descriptive only):
      Mean smoothed lift across the full locked top-N degree set, plus the
      fraction of those degrees clearing FIELD_LIFT_FLOOR. Reported but does
      not drive the classification flag.
    """
    target_col = "High_Target" if target == "High" else "Low_Target"
    w_locked = phase_a_rec["window_locked"]
    n_locked = phase_a_rec["n_locked"]
    peak_degree = phase_a_rec["peak_degree"]

    # Issue 4 guard: if Phase A lock failed, return a clean no_lock record.
    if n_locked == -1:
        out: dict = {
            "feature": feature_col,
            "target": target,
            "window_locked": w_locked,
            "n_locked": -1,
            "peak_degree": peak_degree,
            "locked_top_degrees_n": 0,
            "locked_top_degrees_span": -1,
            "anchor_region_degrees": "[]",
            "phase_b_status": "no_lock_skipped",
        }
        for scheme_name in TEMPORAL_SCHEMES:
            out[f"{scheme_name}_n_persistent"] = 0
            out[f"{scheme_name}_n_total"] = 0
            out[f"{scheme_name}_classification"] = "no_lock"
            out[f"{scheme_name}_blocks"] = "[]"
        out["timestamp_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        out["phase"] = "B"
        out["schema_version"] = SCHEMA_VERSION
        return out

    # Locked top-N degree set (used for secondary field test only).
    global_lift = phase_a_curve_360["Smoothed_Lift"].to_numpy()
    sortable = np.where(np.isnan(global_lift), -np.inf, global_lift)
    locked_top_degrees = set(
        int(d) for d in phase_a_curve_360["Degree"].iloc[
            np.argsort(-sortable)[:n_locked]
        ].tolist()
    )

    # Anchor region: peak_degree +/- ANCHOR_HALF_WIDTH_DEG, computed circularly.
    anchor_degrees = set(
        (peak_degree + offset) % 360
        for offset in range(-ANCHOR_HALF_WIDTH_DEG, ANCHOR_HALF_WIDTH_DEG + 1)
    )

    # Issue 3: log angular span of the locked top-N set (descriptive).
    sorted_degrees = sorted(locked_top_degrees)
    if len(sorted_degrees) >= 2:
        gaps = [sorted_degrees[i + 1] - sorted_degrees[i]
                for i in range(len(sorted_degrees) - 1)]
        gaps.append(360 - sorted_degrees[-1] + sorted_degrees[0])  # wrap
        max_gap = max(gaps)
        locked_top_degrees_span = 360 - max_gap
    else:
        locked_top_degrees_span = 0

    out = {
        "feature": feature_col,
        "target": target,
        "window_locked": w_locked,
        "n_locked": n_locked,
        "peak_degree": peak_degree,
        "locked_top_degrees_n": len(locked_top_degrees),
        "locked_top_degrees_span": int(locked_top_degrees_span),
        "anchor_region_degrees": json.dumps(sorted(anchor_degrees)),
        "phase_b_status": "ran",
    }

    for scheme_name, blocks in TEMPORAL_SCHEMES.items():
        block_records = []
        for block_name, year_start, year_end in blocks:
            db = df[(df["Year"] >= year_start) & (df["Year"] <= year_end)].copy()
            if db.empty:
                block_records.append({
                    "block": block_name, "n_events": 0,
                    "block_baseline": np.nan,
                    "block_baseline_vs_global": np.nan,
                    "anchor_mean_lift": np.nan,
                    "field_mean_lift": np.nan,
                    "field_frac_above": np.nan,
                    "block_persistent": False,
                })
                continue
            block_baseline = db[target_col].mean()
            global_baseline = phase_a_rec["baseline_rate"]
            baseline_vs_global = (
                float(block_baseline / global_baseline)
                if global_baseline > 0 else np.nan
            )
            if block_baseline <= 0:
                block_records.append({
                    "block": block_name, "n_events": int(len(db)),
                    "block_baseline": float(block_baseline),
                    "block_baseline_vs_global": baseline_vs_global,
                    "anchor_mean_lift": np.nan,
                    "field_mean_lift": np.nan,
                    "field_frac_above": np.nan,
                    "block_persistent": False,
                })
                continue

            block_curve = build_degree_lift_table(db, target_col, w_locked)

            # Anchor (PRIMARY): MAX smoothed lift within peak +/- ANCHOR_HALF.
            # v2.0.2 patch: max captures local peak persistence and tolerates
            # the 1-2 degree jitter introduced by smoothing/binning, while
            # mean-based test was over-rejecting strong signals because
            # neighborhood dips dragged the average below 1.15. Verified
            # empirically on G-LON HS: 6/7 blocks show lift >= 1.15 at the
            # exact peak degree, which mean test obscured.
            anchor_mask = block_curve["Degree"].isin(anchor_degrees)
            anchor_lifts = block_curve.loc[anchor_mask, "Smoothed_Lift"].to_numpy()
            anchor_lifts = anchor_lifts[~np.isnan(anchor_lifts)]
            anchor_max = float(np.max(anchor_lifts)) if len(anchor_lifts) else np.nan
            anchor_mean = float(np.mean(anchor_lifts)) if len(anchor_lifts) else np.nan

            # Field (SECONDARY).
            field_mask = block_curve["Degree"].isin(locked_top_degrees)
            field_lifts = block_curve.loc[field_mask, "Smoothed_Lift"].to_numpy()
            field_lifts = field_lifts[~np.isnan(field_lifts)]
            field_mean = float(np.mean(field_lifts)) if len(field_lifts) else np.nan
            field_frac = (
                float(np.mean(field_lifts >= FIELD_LIFT_FLOOR))
                if len(field_lifts) else np.nan
            )

            # PRIMARY classification: anchor max meets the lift floor.
            persistent = bool(
                not np.isnan(anchor_max) and anchor_max >= ANCHOR_LIFT_FLOOR
            )
            block_records.append({
                "block": block_name, "n_events": int(len(db)),
                "block_baseline": float(block_baseline),
                "block_baseline_vs_global": baseline_vs_global,
                "anchor_max_lift": anchor_max,        # PRIMARY
                "anchor_mean_lift": anchor_mean,      # secondary diagnostic
                "field_mean_lift": field_mean,
                "field_frac_above": field_frac,
                "block_persistent": persistent,
            })

        n_persistent_blocks = sum(1 for b in block_records if b["block_persistent"])
        n_total = len(block_records)
        meets_min = n_persistent_blocks >= PERSISTENCE_MIN_BLOCKS[scheme_name]
        meets_anchor = n_persistent_blocks >= PERSISTENCE_ANCHOR_BLOCKS[scheme_name]
        if meets_anchor:
            classification = "anchor"
        elif meets_min:
            classification = "persistent"
        else:
            classification = "fragile"

        out[f"{scheme_name}_n_persistent"] = n_persistent_blocks
        out[f"{scheme_name}_n_total"] = n_total
        out[f"{scheme_name}_classification"] = classification
        out[f"{scheme_name}_blocks"] = json.dumps(block_records)

    out["timestamp_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    out["phase"] = "B"
    out["schema_version"] = SCHEMA_VERSION
    return out


# ============================================================================
# PER-EVENT FEATURE EXTRACTION (ML layer)
# ============================================================================

def per_event_features(df: pd.DataFrame, feature_col: str,
                       hs_curve: pd.DataFrame, hs_peak: int,
                       ls_curve: pd.DataFrame, ls_peak: int) -> pd.DataFrame:
    """
    For each event, compute:
      - event_id (stable: pinned to base_row_index of the source file)
      - date, year
      - feature_name, coordinate_frame
      - raw_degree
      - smoothed_lift_HS / smoothed_lift_LS (full-sample, descriptive)
      - distance_to_peak_HS / distance_to_peak_LS (circular)
      - block_id_7 (7-block scheme — finest partition)

    Full-sample smoothed lift values are descriptive only. For Paper 2 ML use,
    leakage-free smoothed curves must be re-derived per training fold from
    raw_degree; this file's purpose is to preserve the universal inputs
    needed for any future re-derivation.
    """
    hs_lookup = dict(zip(hs_curve["Degree"].astype(int), hs_curve["Smoothed_Lift"]))
    ls_lookup = dict(zip(ls_curve["Degree"].astype(int), ls_curve["Smoothed_Lift"]))

    blocks_7 = TEMPORAL_SCHEMES["7_block"]
    def block_for_year(yr: int) -> str:
        for name, ys, ye in blocks_7:
            if ys <= yr <= ye:
                return name
        return "out_of_range"

    # Extract coordinate frame from feature name (e.g., "Asc x MO G-LON" -> "G-LON";
    # "Asc G-LON x MO G-RA" -> "G-LON_x_G-RA"). Falls back to "unknown" if neither
    # convention matches.
    def extract_frame(name: str) -> str:
        parts = name.split()
        # Same-coordinate: last token is the frame.
        if len(parts) >= 1 and parts[-1].startswith("G-") or parts[-1].startswith("H-"):
            # Also handle cross-coord: "Asc G-LON x MO G-RA" -> two frames.
            frames = [p for p in parts if p.startswith("G-") or p.startswith("H-")]
            if len(frames) == 1:
                return frames[0]
            if len(frames) == 2:
                return f"{frames[0]}_x_{frames[1]}"
        return "unknown"

    coord_frame = extract_frame(feature_col)

    out = pd.DataFrame({
        # Issue 5: event_id is pinned to base_row_index from the source file,
        # so IDs are stable across re-runs and across feature-list expansions.
        "event_id": df["base_row_index"].to_numpy(),
        "date": df[DATE_COL].dt.strftime("%Y-%m-%d").to_numpy(),
        "year": df["Year"].astype(int).to_numpy(),
        "feature_name": feature_col,
        "coordinate_frame": coord_frame,
        "raw_degree": df["Degree"].astype(int).to_numpy(),
    })
    out["smoothed_lift_HS"] = out["raw_degree"].map(hs_lookup).astype(float)
    out["smoothed_lift_LS"] = out["raw_degree"].map(ls_lookup).astype(float)
    out["distance_to_peak_HS"] = out["raw_degree"].apply(lambda d: circ_dist(int(d), hs_peak))
    out["distance_to_peak_LS"] = out["raw_degree"].apply(lambda d: circ_dist(int(d), ls_peak))
    out["block_id_7"] = out["year"].apply(block_for_year)
    return out


# ============================================================================
# DATA LOADING
# ============================================================================

def load_feature(base_file: str, aspect_file: str, feature_col: str) -> pd.DataFrame:
    df_base = pd.read_csv(base_file)
    df_aspect = pd.read_csv(aspect_file)
    if feature_col not in df_aspect.columns:
        raise ValueError(f"'{feature_col}' missing from {aspect_file}.")
    if len(df_base) != len(df_aspect):
        raise ValueError(
            f"Row mismatch: base={len(df_base)} aspect={len(df_aspect)}"
        )
    df = df_base[[DATE_COL, RUNS_COL]].copy()
    # Issue 5: pin stable event_id to the original row index of the source
    # file BEFORE any filtering, so IDs survive future expansions.
    df["base_row_index"] = np.arange(len(df), dtype=np.int64)
    df[feature_col] = df_aspect[feature_col].to_numpy()
    try:
        df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce", format="mixed")
    except (TypeError, ValueError):
        df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
    df["High_Target"] = (df[RUNS_COL] >= HIGH_THRESHOLD).astype(int)
    df["Low_Target"] = (df[RUNS_COL] <= LOW_THRESHOLD).astype(int)
    df = df.dropna(subset=[feature_col]).copy()
    df["Year"] = df[DATE_COL].dt.year
    # Issue 6: hard-fail if year extraction produced NaNs. A silent year
    # collapse would propagate into Phase B as missing-block errors.
    if df["Year"].isna().any():
        n_bad = int(df["Year"].isna().sum())
        raise ValueError(
            f"Year extraction failed for {n_bad} rows — invalid dates present "
            f"in {feature_col}. Aborting before Phase A to avoid silent corruption."
        )
    df["Year"] = df["Year"].astype(int)
    df["Degree"] = (np.floor(df[feature_col]).astype(int)) % 360
    return df


# ============================================================================
# REGISTRY I/O
# ============================================================================

def append_phase_a(rec: dict, json_path: Path, csv_path: Path) -> None:
    if json_path.exists():
        reg = json.loads(json_path.read_text())
    else:
        reg = {"schema_version": SCHEMA_VERSION, "entries": []}
    reg["entries"].append(rec)
    json_path.write_text(json.dumps(reg, indent=2))
    row = pd.DataFrame([rec])
    if csv_path.exists():
        row.to_csv(csv_path, mode="a", header=False, index=False)
    else:
        row.to_csv(csv_path, index=False)


def append_phase_b(rec: dict, csv_path: Path) -> None:
    row = pd.DataFrame([rec])
    if csv_path.exists():
        row.to_csv(csv_path, mode="a", header=False, index=False)
    else:
        row.to_csv(csv_path, index=False)


def update_top_degrees(feature_col: str, target: str,
                       degrees: list[int], json_path: Path) -> None:
    if json_path.exists():
        reg = json.loads(json_path.read_text())
    else:
        reg = {}
    reg.setdefault(feature_col, {})[target] = degrees
    json_path.write_text(json.dumps(reg, indent=2))


# ============================================================================
# RUN MANIFEST
# ============================================================================

def write_run_manifest(manifest_path: Path, manifest: dict) -> None:
    """Append a manifest row recording engine version, files, feature list,
    row counts, skipped features, and timestamp."""
    row = pd.DataFrame([{
        "timestamp_utc": manifest["timestamp_utc"],
        "engine_schema": manifest["engine_schema"],
        "base_file": manifest["base_file"],
        "aspect_file": manifest["aspect_file"],
        "feature_count_requested": manifest["feature_count_requested"],
        "feature_count_succeeded": manifest["feature_count_succeeded"],
        "feature_count_skipped": manifest["feature_count_skipped"],
        "skipped_features_json": json.dumps(manifest["skipped_features"]),
        "succeeded_features_json": json.dumps(manifest["succeeded_features"]),
        "row_counts_json": json.dumps(manifest["row_counts"]),
        "output_dir": str(manifest["output_dir"]),
    }])
    if manifest_path.exists():
        row.to_csv(manifest_path, mode="a", header=False, index=False)
    else:
        row.to_csv(manifest_path, index=False)


# ============================================================================
# ORCHESTRATOR — single feature, full v2.0 pipeline
# ============================================================================

def run_v2_for_feature(df: pd.DataFrame, feature_col: str, output_dir: Path
                       ) -> dict:
    """
    Execute the complete v2.0 pipeline on one feature:
      Phase A (HS + LS) -> Phase B (HS + LS) -> per-event extraction.

    Returns a dict summarizing locks, persistence, and output paths.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "diagnostics").mkdir(exist_ok=True)
    (output_dir / "per_event_features").mkdir(exist_ok=True)

    registry_json = output_dir / "omni_feature_registry.json"
    registry_csv = output_dir / "omni_feature_registry.csv"
    temporal_csv = output_dir / "temporal_persistence.csv"
    top_deg_json = output_dir / "top_degrees_by_feature.json"

    safe = feature_col.replace(" ", "_").replace("/", "_")
    summary: dict = {"feature": feature_col, "targets": {}}
    curves: dict[str, pd.DataFrame] = {}
    peaks: dict[str, int] = {}

    # ---- Phase A for each target -----------------------------------------
    for target in ("High", "Low"):
        rec_a, pl, c360, win_diag = phase_a_target(df, feature_col, target)
        curves[target] = c360
        peaks[target] = rec_a["peak_degree"]

        # Persist diagnostics.
        diag_dir = output_dir / "diagnostics"
        pl["curve"].to_csv(diag_dir / f"{safe}__{target}__lift_vs_N.csv", index=False)
        c360.to_csv(diag_dir / f"{safe}__{target}__smoothed_360.csv", index=False)
        pd.DataFrame(win_diag).to_csv(
            diag_dir / f"{safe}__{target}__window_diag.csv", index=False
        )

        # Record top-N locked degree set.
        global_lift = c360["Smoothed_Lift"].to_numpy()
        sortable = np.where(np.isnan(global_lift), -np.inf, global_lift)
        locked_top = sorted(int(d) for d in c360["Degree"].iloc[
            np.argsort(-sortable)[: rec_a["n_locked"]]
        ].tolist())
        update_top_degrees(feature_col, target, locked_top, top_deg_json)

        append_phase_a(rec_a, registry_json, registry_csv)

        # ---- Phase B for this target --------------------------------------
        rec_b = phase_b_target(df, feature_col, target, rec_a, c360)
        append_phase_b(rec_b, temporal_csv)

        summary["targets"][target] = {"phase_a": rec_a, "phase_b": rec_b}

    # ---- Per-event extraction --------------------------------------------
    per_event = per_event_features(
        df, feature_col,
        curves["High"], peaks["High"],
        curves["Low"], peaks["Low"],
    )
    pe_path = output_dir / "per_event_features" / f"{safe}.csv"
    per_event.to_csv(pe_path, index=False)
    summary["per_event_path"] = str(pe_path)
    summary["per_event_row_count"] = len(per_event)

    return summary


# ============================================================================
# ORCHESTRATOR — batch over a feature list
# ============================================================================

def run_v2_batch(base_file: str, aspect_file: str,
                 feature_list: list[str], output_dir: Path) -> dict:
    """
    Run the v2.0 pipeline on every feature in feature_list, all of which must
    live in the same aspect_file. Records a run manifest at completion.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "run_manifest.csv"

    succeeded: list[str] = []
    skipped: list[dict] = []
    row_counts: dict[str, int] = {}

    for feature_col in feature_list:
        try:
            df = load_feature(base_file, aspect_file, feature_col)
            summary = run_v2_for_feature(df, feature_col, output_dir)
            succeeded.append(feature_col)
            row_counts[feature_col] = summary["per_event_row_count"]
            print(f"  [OK]   {feature_col}  ({summary['per_event_row_count']:,} events)")
        except Exception as exc:
            skipped.append({"feature": feature_col, "error": str(exc)})
            print(f"  [SKIP] {feature_col}  ({exc})")

    manifest = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "engine_schema": SCHEMA_VERSION,
        "base_file": base_file,
        "aspect_file": aspect_file,
        "feature_count_requested": len(feature_list),
        "feature_count_succeeded": len(succeeded),
        "feature_count_skipped": len(skipped),
        "succeeded_features": succeeded,
        "skipped_features": skipped,
        "row_counts": row_counts,
        "output_dir": output_dir,
    }
    write_run_manifest(manifest_path, manifest)
    return manifest



# ============================================================================
# v2.0 SINGLE-FEATURE RUN — Drive persistence (Step B revB, 2026-04-28)
# ----------------------------------------------------------------------------
# Edit BASE_FILE, ASPECT_FILE, FEATURE_NAME below. Output is written directly
# to the Drive workspace. A pre-run snapshot is saved BEFORE engine mutation
# and a post-run snapshot is saved AFTER, with deduplication applied to the
# registry and temporal-persistence CSVs between the two snapshots.
#
# Engine code above (lines 1-762) is byte-identical to v2.0.2; this section
# only changes how outputs are persisted.
# ============================================================================

import datetime as _dt
import shutil
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from google.colab import drive

# ---- Drive mount and canonical paths --------------------------------------
drive.mount('/content/drive', force_remount=False)

DRIVE_BASE = Path('/content/drive/MyDrive/OMNI_PROJECT')
WORKSPACE  = DRIVE_BASE / 'workspace'
ARCHIVES   = DRIVE_BASE / 'archives'
WORKSPACE.mkdir(parents=True, exist_ok=True)
ARCHIVES.mkdir(parents=True, exist_ok=True)

# ---- Snapshot helper ------------------------------------------------------
def _save_snapshot(label: str, manifest_lines: list[str]) -> Path:
    """Copy WORKSPACE -> ARCHIVES/run_<utc>_<label>/, write manifest, return path."""
    run_id = _dt.datetime.now(_dt.UTC).strftime("%Y%m%d_%H%M%S_%f")
    snap = ARCHIVES / f'run_{run_id}_{label}'
    if WORKSPACE.exists():
        shutil.copytree(WORKSPACE, snap)
    else:
        snap.mkdir(parents=True, exist_ok=True)
    (snap / "SNAPSHOT_MANIFEST.txt").write_text(
        f"OMNI snapshot\nUTC timestamp: {run_id}\nLabel: {label}\n"
        + "".join(f"{line}\n" for line in manifest_lines)
    )
    n = sum(1 for _ in snap.rglob('*') if _.is_file())
    print(f"  Snapshot ({label}): {snap.name}  ({n} files)")
    return snap

# ---- Inputs and outputs ---------------------------------------------------
# Input data files remain at /content/ for now; data_raw/ migration deferred.
BASE_FILE     = '/content/drive/MyDrive/MLB 2000-no0224 Training Files by System et al/MLB 2000 - no02-2024 Combined Calcd Positions.csv'
ASPECT_FILE   = '/content/drive/MyDrive/MLB 2000-no0224 Training Files by System et al/MLB 2000-no02-2024 Cross-System G-RA to G-LON.csv'
FEATURE_NAME  = 'Asc G-RA x MO G-LON'
OUTPUT_DIR    = WORKSPACE      # writes go directly to Drive workspace

# ---- Pre-run snapshot -----------------------------------------------------
print("="*78)
print("PRE-RUN SNAPSHOT")
print("="*78)
_save_snapshot('pre', [
    f"Trigger: single-feature run (pre-mutation)",
    f"Feature (planned): {FEATURE_NAME}",
    f"Aspect file: {ASPECT_FILE}",
    f"Workspace: {WORKSPACE}",
])

print(f"\nLoading: {FEATURE_NAME}")
df = load_feature(BASE_FILE, ASPECT_FILE, FEATURE_NAME)
print(f"Rows: {len(df):,} | HS rate: {df['High_Target'].mean():.4f}"
      f" | LS rate: {df['Low_Target'].mean():.4f}")

print("\n" + "="*78)
print(f"PHASE A v2.0 + PHASE B + PER-EVENT EXTRACTION | FEATURE: {FEATURE_NAME}")
print("="*78)

summary = run_v2_for_feature(df, FEATURE_NAME, OUTPUT_DIR)

# ---- Post-run dedupe ------------------------------------------------------
# The engine appends rows by design. Re-running an already-present feature
# would otherwise create duplicates. Drop duplicates by (feature, target),
# keeping the latest entry. This protects the locked-artifact integrity
# without touching engine I/O logic.
print("\n" + "="*78)
print("POST-RUN DEDUPE")
print("="*78)
for csv_name in ('omni_feature_registry.csv', 'temporal_persistence.csv'):
    p = OUTPUT_DIR / csv_name
    if p.exists():
        df_csv = pd.read_csv(p)
        before = len(df_csv)
        df_csv = df_csv.drop_duplicates(subset=['feature', 'target'], keep='last').reset_index(drop=True)
        df_csv.to_csv(p, index=False)
        print(f"  {csv_name}: {before} -> {len(df_csv)} rows")

# Registry JSON also receives append semantics from the engine; dedupe by
# (feature, target) keeping the latest entry. `json` is in scope from engine.
registry_json = OUTPUT_DIR / "omni_feature_registry.json"
if registry_json.exists():
    reg = json.loads(registry_json.read_text())
    entries = reg.get("entries", [])
    deduped = {}
    for e in entries:
        key = (e.get("feature"), e.get("target"))
        deduped[key] = e  # keep latest
    reg["entries"] = list(deduped.values())
    registry_json.write_text(json.dumps(reg, indent=2))
    print(f"  omni_feature_registry.json: {len(entries)} -> {len(reg['entries'])} entries")

# Console summary.
for target in ('High', 'Low'):
    a = summary['targets'][target]['phase_a']
    b = summary['targets'][target]['phase_b']
    print(f"\n--- {target} ---  [Phase A]")
    for k in ['window_locked','n_locked','peak_degree','peak_smoothed_lift',
              'peak_smoothed_count','window_drift_deg','peaks_within_5_of_lock',
              'scale_structure_flag','n_core_kneedle','n_asymptote_95',
              'n_asymptote_99','baseline_rate']:
        v = a[k]
        print(f"  {k:<24s}: {v:.4f}" if isinstance(v,float) else f"  {k:<24s}: {v}")
    print(f"--- {target} ---  [Phase B]")
    for scheme in ('3_block','5_block','7_block'):
        n_p = b[f'{scheme}_n_persistent']; n_t = b[f'{scheme}_n_total']
        cls = b[f'{scheme}_classification']
        print(f"  {scheme:<10s}: {n_p}/{n_t} blocks persistent  ->  {cls}")

# Plots — same format as v1.5.
import json as _json
import pandas as _pd
for target in ('High','Low'):
    a = summary['targets'][target]['phase_a']
    safe = FEATURE_NAME.replace(' ','_').replace('/','_')
    c360 = _pd.read_csv(OUTPUT_DIR / 'diagnostics' / f"{safe}__{target}__smoothed_360.csv")
    lvn  = _pd.read_csv(OUTPUT_DIR / 'diagnostics' / f"{safe}__{target}__lift_vs_N.csv")

    fig, ax = plt.subplots(figsize=(14,4))
    ax.plot(c360['Degree'], c360['Smoothed_Lift'], lw=1.2)
    ax.axhline(1.0, ls='--', lw=0.8, color='gray')
    ax.axvline(a['peak_degree'], ls=':', lw=0.8, color='red',
               label=f"peak deg = {a['peak_degree']} (lift {a['peak_smoothed_lift']:.3f}, n={int(a['peak_smoothed_count'])})")
    ax.set_xlim(0,359); ax.set_xlabel('Degree'); ax.set_ylabel('Smoothed Lift')
    ax.set_title(f"{FEATURE_NAME} | {target} | window={a['window_locked']}deg "
                 f"| {a['scale_structure_flag']} (drift={a['window_drift_deg']}deg)")
    ax.legend(loc='upper right'); plt.tight_layout(); plt.show()

    fig, ax = plt.subplots(figsize=(11,4))
    ax.plot(lvn['N'], lvn['Pct_Above1_Signal'], lw=1.5)
    if a['n_core_kneedle']: ax.axvline(a['n_core_kneedle'], color='gray',   ls=':',  label=f"core/knee N={a['n_core_kneedle']}")
    if a['n_asymptote_95']: ax.axvline(a['n_asymptote_95'], color='orange', ls=':',  label=f"95% N={a['n_asymptote_95']}")
    if a['n_locked'] != -1: ax.axvline(a['n_locked'],       color='green',  ls='--', lw=2, label=f"LOCK (98%) N={a['n_locked']}")
    if a['n_asymptote_99']: ax.axvline(a['n_asymptote_99'], color='red',    ls=':',  label=f"99% N={a['n_asymptote_99']}")
    ax.axhline(98.0, color='green', ls=':', lw=0.6)
    ax.set_xlabel('Top-N (degrees)'); ax.set_ylabel('% Above-Baseline Signal Captured')
    ax.set_title(f"{FEATURE_NAME} | {target} | Signal Capture vs N")
    ax.legend(loc='lower right'); plt.tight_layout(); plt.show()

print("\n" + "="*78)
print(f"OUTPUTS WRITTEN TO: {OUTPUT_DIR}")
print("="*78)

# ---- Post-run snapshot ----------------------------------------------------
print("\n" + "="*78)
print("POST-RUN SNAPSHOT")
print("="*78)
_save_snapshot('post', [
    f"Trigger: single-feature run (post-dedupe)",
    f"Feature: {FEATURE_NAME}",
    f"Aspect file: {ASPECT_FILE}",
    f"Workspace: {WORKSPACE}",
])
