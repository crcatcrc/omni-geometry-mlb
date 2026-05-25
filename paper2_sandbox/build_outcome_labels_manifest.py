"""
OMNI Paper 2 Sandbox — outcome-class label manifest construction — v1.0.

Builds outcome_labels_manifest_v1_0.csv with per-event outcome labels for
both the total-runs family (HS, LS, MID) and the margin-polarity family
(BHW, GHL, MID), per Charter §5.1 operational definitions.

Source: any cross-system master file in
/content/drive/MyDrive/MLB 2000-no0224 Training Files by System et al/
(all carry the same per-game metadata: Date, Home/Away scores, Total Runs).
Row order in those files corresponds to event_id order in
per_event_features/ files. This is verified by date cross-check before
classification.

Charter §5.1 thresholds:
  HS:  Total Runs Scored >= 16     LS:  Total Runs Scored <= 3
  BHW: home_margin >= +5           GHL: home_margin <= -5

Tier 1 Step 1 artifact per Charter §4.1.
"""

from pathlib import Path
import hashlib
import pandas as pd

SANDBOX_ROOT = Path("/content/drive/MyDrive/OMNI_PROJECT/paper2_sandbox")
GATE_DIR = SANDBOX_ROOT / "CONFIRMATORY_GATE"
SENTINEL = GATE_DIR / "sandbox_seal_v1_0.lock"
LABELS_PATH = SANDBOX_ROOT / "outcome_labels_manifest_v1_0.csv"

CROSS_SYSTEM_SOURCE = Path(
    "/content/drive/MyDrive/MLB 2000-no0224 Training Files by System et al/"
    "MLB 2000-no02-2024 Cross-System G-LON to G-AZ.csv"
)
PER_EVENT_SOURCE = Path(
    "/content/drive/MyDrive/OMNI_PROJECT/workspace/per_event_features/Asc_x_MO_G-LON.csv"
)
STRATUM_PATH = SANDBOX_ROOT / "event_stratum_manifest_v1_0.csv"

# --- Sanity ------------------------------------------------------------------
assert SENTINEL.exists(), (
    f"Sentinel not found: {SENTINEL}\n"
    "Do not proceed unless the confirmatory hold-out has been sealed."
)
assert CROSS_SYSTEM_SOURCE.exists(), f"Cross-system source not found: {CROSS_SYSTEM_SOURCE}"
assert PER_EVENT_SOURCE.exists(), f"Per-event source not found: {PER_EVENT_SOURCE}"
assert not LABELS_PATH.exists(), (
    f"Outcome-labels manifest already exists at {LABELS_PATH}. "
    "Construction is one-shot; do not regenerate. Create v1_1 if revision needed."
)

# --- Charter §5.1 thresholds -------------------------------------------------
HS_THRESHOLD = 16
LS_THRESHOLD = 3
BHW_THRESHOLD = 5
GHL_THRESHOLD = -5

# --- Load cross-system metadata ----------------------------------------------
print("Loading cross-system metadata...")
needed_cols = ["Date", "Home Team Score", "Away Team Score", "Total Runs Scored"]
master = pd.read_csv(CROSS_SYSTEM_SOURCE, usecols=needed_cols)

# Mixed date formats in the source file: predominantly "29-Mar-00" (d-MMM-yy)
# with a subset in "May 19 2021" (MMM d yyyy) form. Parse primary format,
# fall back for the rest, fail loudly if any remain unparseable.
dates = pd.to_datetime(master["Date"], format="%d-%b-%y", errors="coerce")
mask = dates.isna()
if mask.any():
    print(f"Note: {mask.sum():,} dates not in %d-%b-%y form; using fallback parser.")
    alt = pd.to_datetime(master.loc[mask, "Date"], errors="coerce")
    dates.loc[mask] = alt
if dates.isna().any():
    bad = master.loc[dates.isna(), "Date"].head(10).tolist()
    raise ValueError(f"Unparseable dates remain (first 10): {bad}")
master["Date"] = dates
print(f"Loaded: {len(master):,} games")

assert len(master) == 57635, (
    f"Expected 57,635 games; found {len(master):,}. Check source file integrity."
)

# event_id is the 0-indexed row order of the cross-system file
master = master.reset_index().rename(columns={"index": "event_id"})

# --- Date cross-check against per-event file ---------------------------------
print("\nCross-checking dates against per-event file (event_id alignment)...")
per_event = pd.read_csv(PER_EVENT_SOURCE, usecols=["event_id", "date"])
per_event["date"] = pd.to_datetime(per_event["date"], errors="raise")
merged = master[["event_id", "Date"]].merge(
    per_event[["event_id", "date"]], on="event_id", how="inner"
)
if len(merged) != 57635:
    raise RuntimeError(
        f"event_id join produced {len(merged):,} rows; expected 57,635. "
        "event_id semantics differ between sources; do not proceed."
    )
mismatch = merged[merged["Date"] != merged["date"]]
if len(mismatch) > 0:
    print(f"WARNING: {len(mismatch)} date mismatches:")
    print(mismatch.head(10))
    raise RuntimeError(
        "Date alignment failed. event_id semantics differ; do not proceed."
    )
print(f"Date alignment verified across all {len(merged):,} events.")

# --- Compute outcome labels --------------------------------------------------
master["home_margin"] = master["Home Team Score"] - master["Away Team Score"]

def total_runs_class(t):
    if t >= HS_THRESHOLD: return "HS"
    if t <= LS_THRESHOLD: return "LS"
    return "MID"

def margin_polarity_class(m):
    if m >= BHW_THRESHOLD: return "BHW"
    if m <= GHL_THRESHOLD: return "GHL"
    return "MID"

master["total_runs_class"] = master["Total Runs Scored"].map(total_runs_class)
master["margin_polarity_class"] = master["home_margin"].map(margin_polarity_class)

# --- Diagnostics -------------------------------------------------------------
print("\n=== Total-runs class (Charter §5.1: HS ≥ 16, LS ≤ 3) ===")
print(master["total_runs_class"].value_counts())
print(f"HS fraction:  {(master['total_runs_class'] == 'HS').mean():.4f}")
print(f"LS fraction:  {(master['total_runs_class'] == 'LS').mean():.4f}")

print("\n=== Margin-polarity class (Charter §5.1: BHW ≥ +5, GHL ≤ -5) ===")
print(master["margin_polarity_class"].value_counts())
print(f"BHW fraction: {(master['margin_polarity_class'] == 'BHW').mean():.4f}")
print(f"GHL fraction: {(master['margin_polarity_class'] == 'GHL').mean():.4f}")

print("\nTotal-runs distribution:")
print(master["Total Runs Scored"].describe())

print("\nHome-margin distribution:")
print(master["home_margin"].describe())

# --- Joint outcome × stratum cross-tabs (Tier 1 Step 1 sample-balance audit)
if STRATUM_PATH.exists():
    print("\n=== Joint outcome × stratum (8-cell panel; uses locked stratum manifest) ===")
    strat = pd.read_csv(STRATUM_PATH)
    joint = master.merge(strat, on="event_id")

    print("\nTotal-runs class × stratum:")
    print(pd.crosstab(joint["total_runs_class"], joint["stratum"], margins=True))

    print("\nMargin-polarity class × stratum:")
    print(pd.crosstab(joint["margin_polarity_class"], joint["stratum"], margins=True))
else:
    print("\nStratum manifest not yet present; skipping joint cross-tab.")

# --- Write manifest ----------------------------------------------------------
out = master[["event_id", "Total Runs Scored", "home_margin",
              "total_runs_class", "margin_polarity_class"]].rename(
    columns={"Total Runs Scored": "total_runs"}
)
out.to_csv(LABELS_PATH, index=False)

with open(LABELS_PATH, "rb") as f:
    labels_sha256 = hashlib.sha256(f.read()).hexdigest()

print(f"\nWritten: {LABELS_PATH}")
print(f"Total events: {len(out)}")
print(f"\nManifest SHA256 (commit to GitHub as outcome_labels_manifest_v1_0.sha256.txt):")
print(labels_sha256)
