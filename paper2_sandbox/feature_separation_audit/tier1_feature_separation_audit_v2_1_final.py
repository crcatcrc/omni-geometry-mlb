"""
OMNI Paper 2 Sandbox — Tier 1: Feature Separation Audit v2.1 (final).
Same-slate / Δt-binned audit using true UTC start times.

velocity_robust_deg_per_hr = (median separation in the 45–90 min bin)
                           / (median Δt in the 45–90 min bin, in hours).
Single-bin ratio: stable denominator (~1 hr), directly operational, no
small-denominator artifact. near45_sep_median remains the anchor metric;
operational_scale_flag is descriptive only.

Timing source: MLB 2000 - no02-2024 Combined Calcd Positions.csv
Uses Game_DateTime_UTC. Join: ROW_ORDER -> event_id = row index (verified).
"""

from pathlib import Path
import hashlib
import numpy as np
import pandas as pd

# --- Paths ------------------------------------------------------------------
SANDBOX_ROOT  = Path("/content/drive/MyDrive/OMNI_PROJECT/paper2_sandbox")
SENTINEL      = SANDBOX_ROOT / "CONFIRMATORY_GATE" / "sandbox_seal_v1_0.lock"
PER_EVENT_DIR = Path("/content/drive/MyDrive/OMNI_PROJECT/workspace/per_event_features")
HOLDOUT_PATH  = SANDBOX_ROOT / "holdout_manifest_v1_0.csv"
TIMING_SOURCE = Path(
    "/content/drive/MyDrive/MLB 2000-no0224 Training Files by System et al/"
    "MLB 2000 - no02-2024 Combined Calcd Positions.csv"
)
OUTPUT_DIR    = SANDBOX_ROOT / "tier1_feature_separation_audit_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Configuration ----------------------------------------------------------
USE_EXPLORATORY_ONLY = True
FAST_POINTS      = {"Asc", "MC", "VX", "EA", "MO"}
DT_EDGES_MIN     = [15, 30, 45, 90, 180, 360]
DT_LABELS        = ["<=15", "15-30", "30-45", "45-90", "90-180", "180-360", ">360"]
VEL_BIN_IDX      = 3              # the "45-90" min bin, used for velocity_robust
MIN_BIN_PAIRS    = 50
NEARCONC_MAX_MIN = 45
SMOOTH_REF_DEG   = 5
TIMING_UTC_COL   = "Game_DateTime_UTC"
TIMING_DATE_COL  = "Date"

# --- Sanity -----------------------------------------------------------------
assert SENTINEL.exists(),      f"Confirmatory seal not found: {SENTINEL}"
assert PER_EVENT_DIR.exists(), f"Per-event dir not found: {PER_EVENT_DIR}"
assert HOLDOUT_PATH.exists(),  f"Holdout manifest not found: {HOLDOUT_PATH}"
assert TIMING_SOURCE.exists(), f"Timing source not found: {TIMING_SOURCE}"

# --- Helpers ----------------------------------------------------------------
def parse_dates(s):
    try:
        return pd.to_datetime(s, errors="coerce", format="mixed")
    except (TypeError, ValueError):
        return pd.to_datetime(s, errors="coerce")

def circ_sep(a, b):
    d = np.abs(a - b) % 360
    return np.minimum(d, 360 - d)

def circ_mean_deg(deg):
    ang = np.angle(np.mean(np.exp(1j * np.deg2rad(deg))))
    return np.rad2deg(ang) % 360

def parse_feature_id(feature_name, fname, coord_frame):
    frame = str(coord_frame).strip()
    origin = body = None
    if isinstance(feature_name, str) and " x " in feature_name:
        h = feature_name.split(" x ")
        origin = h[0].strip()
        body = h[1].split()[0].strip()
    if origin is None or body is None:
        s = fname.replace("_x_", "|").split("|")
        if len(s) == 2:
            origin = origin or s[0]
            body = body or s[1].rsplit("_", 1)[0]
    return origin, body, frame

def include_feature(origin, body, frame):
    if str(frame).upper().replace("-", "") == "GAZ":
        return True
    return (origin in FAST_POINTS) or (body in FAST_POINTS)

# --- Exploratory partition --------------------------------------------------
if USE_EXPLORATORY_ONLY:
    holdout = pd.read_csv(HOLDOUT_PATH)
    explor_dates = set(holdout.loc[holdout["partition"] == "exploratory", "game_date"].astype(str))
    print(f"Exploratory partition: {len(explor_dates):,} game-dates.")
else:
    explor_dates = None
    print("Running on all dates. Confirmatory geometry will be included.")

# --- Build UTC timing lookup with mandatory row-order alignment check --------
REQUIRED = {"event_id", "date", "raw_degree", "coordinate_frame"}
tsrc = pd.read_csv(TIMING_SOURCE)
assert TIMING_UTC_COL in tsrc.columns,  f"{TIMING_UTC_COL!r} not in timing file."
assert TIMING_DATE_COL in tsrc.columns, f"{TIMING_DATE_COL!r} not in timing file."
tsrc = tsrc.reset_index(drop=True)
tsrc["event_id"] = tsrc.index
ref = next((p for p in sorted(PER_EVENT_DIR.glob("*_x_*.csv"))
            if REQUIRED.issubset(pd.read_csv(p, nrows=1).columns)), None)
assert ref is not None, "No reference per-event file for alignment check."
refdf = pd.read_csv(ref, usecols=["event_id", "date"]).set_index("event_id")
t_date = parse_dates(tsrc[TIMING_DATE_COL]).dt.strftime("%Y-%m-%d")
r_date = parse_dates(refdf["date"]).dt.strftime("%Y-%m-%d")
common = r_date.index.intersection(pd.Index(tsrc["event_id"]))
mismatch = int((r_date.loc[common].values != t_date.iloc[common].values).sum())
assert mismatch == 0, (f"ROW-ORDER MISALIGNMENT: {mismatch} mismatches vs {ref.name}. Unsafe.")
print(f"Row-order alignment verified vs {ref.name}: 0 date mismatches over {len(common):,} events.")
utc = pd.to_datetime(tsrc[TIMING_UTC_COL], errors="coerce", utc=True)
timing = pd.DataFrame({"event_id": tsrc["event_id"], "utc": utc}).dropna()
print(f"Timing lookup: {len(timing):,} events with UTC start instants.")

# --- Locate valid per-event feature files -----------------------------------
valid = []
for p in sorted(PER_EVENT_DIR.glob("*_x_*.csv")):
    try:
        head = pd.read_csv(p, nrows=1)
    except Exception:
        continue
    if REQUIRED.issubset(head.columns):
        valid.append(p)
print(f"\n{len(valid)} valid per-event files found.")
assert valid, "No valid per-event files found."

# --- Main audit loop --------------------------------------------------------
master_rows, bin_rows, drift_rows = [], [], []

for fpath in valid:
    head = pd.read_csv(fpath, nrows=1)
    usecols = [c for c in ["event_id", "date", "raw_degree", "coordinate_frame", "feature_name"]
               if c in head.columns]
    df = pd.read_csv(fpath, usecols=usecols)
    feat = df["feature_name"].iloc[0] if "feature_name" in df.columns else fpath.stem
    origin, body, frame = parse_feature_id(feat, fpath.stem, df["coordinate_frame"].iloc[0])
    if not include_feature(origin, body, frame):
        continue
    is_az = str(frame).upper().replace("-", "") == "GAZ"

    df["date_iso"] = parse_dates(df["date"]).dt.strftime("%Y-%m-%d")
    df = df.dropna(subset=["date_iso", "raw_degree"])
    if USE_EXPLORATORY_ONLY:
        df = df[df["date_iso"].isin(explor_dates)]
    df["raw_degree"] = df["raw_degree"].astype(int) % 360
    df = df.merge(timing, on="event_id", how="inner")
    if len(df) < 100:
        continue

    sep_pool, dt_pool = [], []
    for _, g in df.groupby("date_iso"):
        if len(g) < 2:
            continue
        deg = g["raw_degree"].to_numpy()
        t = pd.to_datetime(g["utc"], utc=True).to_numpy(dtype="datetime64[ns]")
        iu = np.triu_indices(deg.size, k=1)
        sep_pool.append(circ_sep(deg[:, None], deg[None, :])[iu])
        dt_minutes = np.abs((t[:, None] - t[None, :]) / np.timedelta64(1, "m"))
        dt_pool.append(dt_minutes[iu])
    if not sep_pool:
        continue
    sep = np.concatenate(sep_pool)
    dt = np.concatenate(dt_pool)
    near = sep[dt <= NEARCONC_MAX_MIN]
    bidx = np.digitize(dt, DT_EDGES_MIN)

    # --- per-Δt-bin profile (records dt_median_min for recomputability) ------
    for bi, lab in enumerate(DT_LABELS):
        m = (bidx == bi)
        s = sep[m]
        dts = dt[m]
        bin_rows.append({
            "origin": origin, "body": body, "frame": frame, "dt_bin": lab,
            "n_pairs": int(s.size),
            "dt_median_min": float(np.median(dts)) if dts.size else np.nan,
            "sep_median": float(np.median(s)) if s.size else np.nan,
            "sep_p90": float(np.percentile(s, 90)) if s.size else np.nan,
        })

    # --- velocity_robust: 45–90 min bin ratio --------------------------------
    mv = (bidx == VEL_BIN_IDX)
    if mv.sum() >= MIN_BIN_PAIRS:
        med_dt_hr = np.median(dt[mv]) / 60.0
        velocity_robust = float(np.median(sep[mv]) / med_dt_hr) if med_dt_hr > 0 else np.nan
    else:
        velocity_robust = np.nan

    # --- between-date drift (slow timescale; G-LON/G-RA only) ----------------
    drift_med = np.nan
    if not is_az:
        by_date = (df.groupby("date_iso")["raw_degree"]
                     .apply(lambda x: circ_mean_deg(x.to_numpy())).sort_index())
        if len(by_date) >= 2:
            ord_days = pd.to_datetime(by_date.index).map(pd.Timestamp.toordinal).to_numpy()
            vals = by_date.to_numpy()
            day_delta = np.diff(ord_days)
            dtheta = circ_sep(vals[1:], vals[:-1])
            ok = day_delta > 0
            drift = np.abs(dtheta[ok] / day_delta[ok])
            if drift.size:
                drift_med = float(np.median(drift))
                drift_rows.append({
                    "origin": origin, "body": body, "frame": frame,
                    "n_drift": int(drift.size),
                    "drift_med_deg_per_day": drift_med,
                    "drift_p90_deg_per_day": float(np.percentile(drift, 90)),
                })

    near_med = float(np.median(near)) if near.size else np.nan
    near_p90 = float(np.percentile(near, 90)) if near.size else np.nan
    if np.isnan(near_med):
        flag = "insufficient-near-concurrent"
    elif near_med >= SMOOTH_REF_DEG:
        flag = "same-slate-discriminator"
    elif near_med >= 1.0:
        flag = "marginal"
    else:
        flag = "slow-contextual"

    master_rows.append({
        "origin": origin, "body": body, "frame": frame, "file": fpath.stem,
        "n_events": int(len(df)), "n_pairs": int(sep.size), "n_near45": int(near.size),
        "near45_sep_median": near_med, "near45_sep_p90": near_p90,
        "velocity_robust_deg_per_hr": velocity_robust,
        "samedate_sep_median": float(np.median(sep)),
        "samedate_sep_p90": float(np.percentile(sep, 90)),
        "daily_drift_med_deg_per_day": drift_med,
        "operational_scale_flag": flag,
    })
    print(f"{origin:>3} x {body:<3} {frame:6s} | near<=45m med {near_med:6.2f}° "
          f"| near<=45m p90 {near_p90:6.2f}° | v_robust {velocity_robust:6.2f}°/hr | {flag}")

# --- Write artifacts --------------------------------------------------------
master = pd.DataFrame(master_rows).sort_values(
    ["operational_scale_flag", "near45_sep_median"], ascending=[True, False])
binsdf = pd.DataFrame(bin_rows)
driftdf = pd.DataFrame(drift_rows)
master_path = OUTPUT_DIR / "feature_separation_audit_master.csv"
bins_path   = OUTPUT_DIR / "feature_separation_audit_dt_bins.csv"
drift_path  = OUTPUT_DIR / "feature_separation_audit_drift.csv"
master.to_csv(master_path, index=False)
binsdf.to_csv(bins_path, index=False)
driftdf.to_csv(drift_path, index=False)

print("\n=== Feature Separation Audit v2.1 master table ===")
with pd.option_context("display.max_rows", None, "display.width", 220,
                       "display.float_format", "{:.3f}".format):
    print(master.to_string(index=False))
with open(master_path, "rb") as f:
    sha = hashlib.sha256(f.read()).hexdigest()
print(f"\nMaster CSV SHA256:\n{sha}")
print(f"\nWritten:\n  {master_path}\n  {bins_path}\n  {drift_path}")
print("\n=== Feature Separation Audit v2.1 complete ===")
