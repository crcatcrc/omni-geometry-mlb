"""
OMNI Paper 2 Sandbox — sentinel placement and exploratory-partition loader.

Run in Colab once after generate_holdout_partition.py has produced the
manifest. The sentinel `sandbox_seal_v1_0.lock` declares the confirmatory
hold-out SEALED. It is removed by hand only after the Paper 2 pre-registration
is locked on OSF.

Charter §3 (sealing of the hold-out) is the authoritative reference.
"""

from pathlib import Path
import pandas as pd

SANDBOX_ROOT = Path("/content/drive/MyDrive/OMNI_PROJECT/paper2_sandbox")
GATE_DIR = SANDBOX_ROOT / "CONFIRMATORY_GATE"
SENTINEL = GATE_DIR / "sandbox_seal_v1_0.lock"
MANIFEST_PATH = SANDBOX_ROOT / "holdout_manifest_v1_0.csv"

if not SENTINEL.exists():
    SENTINEL.write_text(
        "OMNI Paper 2 sandbox confirmatory hold-out — SEALED\n"
        "Remove only after Paper 2 pre-registration is locked on OSF.\n"
    )
    print(f"Sentinel created: {SENTINEL}")
else:
    print(f"Sentinel already in place: {SENTINEL}")


def load_exploratory_events(per_event_csv_path, date_col="date"):
    """
    Read a Paper 1 per-event artifact and return only rows whose game-date
    is in the exploratory partition. Refuses to operate if the sentinel is
    absent (i.e. the hold-out has been opened).
    """
    if not SENTINEL.exists():
        raise RuntimeError(
            "Confirmatory sentinel is missing. The hold-out has been opened. "
            "Sandbox notebooks must not run."
        )
    manifest = pd.read_csv(MANIFEST_PATH)
    explor_dates = set(
        manifest.loc[manifest["partition"] == "exploratory", "game_date"]
    )
    df = pd.read_csv(per_event_csv_path)
    df["_date_iso"] = pd.to_datetime(df[date_col]).dt.strftime("%Y-%m-%d")
    df = df[df["_date_iso"].isin(explor_dates)].drop(columns="_date_iso")
    return df.reset_index(drop=True)


# Self-test against a known Paper 1 artifact
SELF_TEST = Path("/content/drive/MyDrive/OMNI_PROJECT/workspace/per_event_features/Asc_x_MO_G-LON.csv")
if SELF_TEST.exists():
    expl = load_exploratory_events(SELF_TEST)
    print(f"Self-test: {len(expl)} exploratory events loaded from {SELF_TEST.name}")
