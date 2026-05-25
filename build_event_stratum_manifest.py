"""
OMNI Paper 2 Sandbox — event-stratum manifest construction (RS / PS) — v0.2.

Classifies each event_id as "regular_season" or "post_season" based on an
authoritative per-year postseason opening-date table sourced by the PI from
MLB.com and Wikipedia (25 May 2026), with 2001 manually verified against
the post-9/11-delayed schedule. The cutoff rule: any game on or after a
year's PS opening date is post_season; otherwise regular_season.

This handles correctly:
  - September wild-card starts (2003, 2011, 2020)
  - Late October / early November World Series games
  - Regular-season tie-breaker games played after game 162
  - The 9/11-delayed 2001 postseason (opening pushed to Oct 9)

Charter §5.2 (Stratification axes) is the authoritative reference.
Sample expectations: ~56,700 RS events; ~800-900 PS events across 2000-2024.

Tier 1 Step 1 artifact per Charter §4.1.
"""

from pathlib import Path
import hashlib
import pandas as pd

SANDBOX_ROOT = Path("/content/drive/MyDrive/OMNI_PROJECT/paper2_sandbox")
GATE_DIR = SANDBOX_ROOT / "CONFIRMATORY_GATE"
SENTINEL = GATE_DIR / "sandbox_seal_v1_0.lock"
STRATUM_PATH = SANDBOX_ROOT / "event_stratum_manifest_v1_0.csv"
EVENT_SOURCE = Path(
    "/content/drive/MyDrive/OMNI_PROJECT/workspace/per_event_features/Asc_x_MO_G-LON.csv"
)

# --- Sanity ------------------------------------------------------------------
assert SENTINEL.exists(), (
    f"Sentinel not found: {SENTINEL}\n"
    "Do not proceed unless the confirmatory hold-out has been sealed."
)
assert EVENT_SOURCE.exists(), f"Event source not found: {EVENT_SOURCE}"
assert not STRATUM_PATH.exists(), (
    f"Stratum manifest already exists at {STRATUM_PATH}. "
    "Construction is one-shot; do not regenerate. If revision is needed, "
    "create v1_1."
)

# --- Authoritative PS opening dates -----------------------------------------
# Sourced 25 May 2026 by PI from MLB.com press releases and per-season
# Wikipedia postseason articles. 2001 manually verified to Oct 9 (9/11 delay).
# Any game on or after the listed date is post_season.
PS_OPENING = {
    2000: "2000-10-03", 2001: "2001-10-09", 2002: "2002-10-01",
    2003: "2003-09-30", 2004: "2004-10-05", 2005: "2005-10-04",
    2006: "2006-10-03", 2007: "2007-10-03", 2008: "2008-10-01",
    2009: "2009-10-07", 2010: "2010-10-06", 2011: "2011-09-30",
    2012: "2012-10-05", 2013: "2013-10-01", 2014: "2014-10-01",
    2015: "2015-10-07", 2016: "2016-10-04", 2017: "2017-10-03",
    2018: "2018-10-02", 2019: "2019-10-01", 2020: "2020-09-29",
    2021: "2021-10-05", 2022: "2022-10-07", 2023: "2023-10-03",
    2024: "2024-10-01",
}
PS_OPENING = {y: pd.Timestamp(d) for y, d in PS_OPENING.items()}

# --- Load events -------------------------------------------------------------
events = pd.read_csv(EVENT_SOURCE, usecols=["event_id", "date"])
events["date"] = pd.to_datetime(events["date"], errors="raise")
events["year"] = events["date"].dt.year

before = len(events)
events = events.drop_duplicates(subset=["event_id"]).reset_index(drop=True)
after = len(events)
print(f"Rows loaded:    {before:,}")
print(f"Unique events:  {after:,}")

assert after == 57635, (
    f"Expected 57,635 unique events (locked Paper 1 event base); found {after:,}. "
    "Check source file integrity."
)

# --- Classify ----------------------------------------------------------------
def classify(row):
    cutoff = PS_OPENING.get(row["year"])
    if cutoff is None:
        return "UNKNOWN_YEAR"
    return "post_season" if row["date"] >= cutoff else "regular_season"

events["stratum"] = events.apply(classify, axis=1)

# --- Diagnostics -------------------------------------------------------------
print("\nStratum counts:")
print(events["stratum"].value_counts())

n_unknown = (events["stratum"] == "UNKNOWN_YEAR").sum()
if n_unknown > 0:
    print(f"\nWARNING: {n_unknown} events with no PS cutoff defined for their year.")
    print(events.loc[events["stratum"] == "UNKNOWN_YEAR", "year"].drop_duplicates())

ps_frac = (events["stratum"] == "post_season").mean()
print(f"\nPS fraction:    {ps_frac:.4f}")

print("\nPer-year stratum counts:")
yearly = events.groupby(["year", "stratum"]).size().unstack(fill_value=0)
print(yearly)

if "post_season" in yearly.columns:
    ps_per_year = yearly["post_season"]
    print("\nPer-year PS count summary:")
    print(f"  Min:  {ps_per_year.min()} (year {ps_per_year.idxmin()})")
    print(f"  Max:  {ps_per_year.max()} (year {ps_per_year.idxmax()})")
    print(f"  Mean: {ps_per_year.mean():.1f}")

# --- Write manifest (Charter §5.2 schema: event_id, stratum) -----------------
events[["event_id", "stratum"]].to_csv(STRATUM_PATH, index=False)

with open(STRATUM_PATH, "rb") as f:
    stratum_sha256 = hashlib.sha256(f.read()).hexdigest()

print(f"\nWritten: {STRATUM_PATH}")
print(f"Total events: {len(events)}")
print(f"\nManifest SHA256 (commit to GitHub as event_stratum_manifest_v1_0.sha256.txt):")
print(stratum_sha256)
