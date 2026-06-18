# HS/LS MODELING UNIVERSE MANIFESTS v1.7
from pathlib import Path
import pandas as pd
import numpy as np
import hashlib
from datetime import datetime, timezone

SANDBOX = Path("/content/drive/MyDrive/OMNI_PROJECT/paper2_sandbox")
IN = SANDBOX / "MASTER_ASPECT_FEATURE_DECISION_VIEW_v1_6.csv"
OUT_A = SANDBOX / "HS_LS_UNIVERSE_A_TIER_A_ENGINE_MANIFEST_v1_7.csv"
OUT_B = SANDBOX / "HS_LS_UNIVERSE_B_TIER_ABC_ENGINE_MANIFEST_v1_7.csv"
OUT_C = SANDBOX / "HS_LS_UNIVERSE_C_REPRESENTATION_DEVELOPMENT_MANIFEST_v1_7.csv"
OUT_QA = SANDBOX / "HS_LS_MODELING_UNIVERSE_MANIFESTS_QA_v1_7.csv"
OUT_TXT = SANDBOX / "HS_LS_MODELING_UNIVERSE_MANIFESTS_SUMMARY_v1_7.txt"

def sha256_file(path, block_size=1024 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            h.update(block)
    return h.hexdigest()

def bool_clean(x):
    if isinstance(x, bool):
        return x
    if pd.isna(x):
        return False
    s = str(x).strip().lower()
    if s in {"true", "1", "yes", "y", "t"}:
        return True
    if s in {"false", "0", "no", "n", "f", "", "nan"}:
        return False
    try:
        return float(s) != 0.0
    except Exception:
        return False

input_sha256 = sha256_file(IN)
run_timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
registry_build_seed = "20260615"

v = pd.read_csv(IN, low_memory=False)

for c in [
    "engine_candidate_pool", "representation_development_pool", "has_HS_fields", "has_LS_fields",
    "has_BHW_fields", "has_GHL_fields", "descriptor_evidence_only",
    "requires_oof_validation_before_candidate_selection", "safe_for_direct_predictive_claim"
]:
    v[c] = v[c].map(bool_clean)

A = v[(v["engine_candidate_pool"]) & (v["coverage_tier_normalized"] == "Tier A")].copy()
B = v[(v["engine_candidate_pool"]) & (v["coverage_tier_normalized"].isin(["Tier A", "Tier B", "Tier C"]))].copy()
C = v[(v["representation_development_pool"])].copy()

def stamp_manifest(df, universe_id, universe_name, modeling_role, rule_text):
    out = df.copy()
    out["modeling_universe_id"] = universe_id
    out["modeling_universe_name"] = universe_name
    out["modeling_role"] = modeling_role
    out["modeling_universe_rule"] = rule_text
    out["universe_manifest_version"] = "v1.7"
    out["universe_manifest_input_sha256"] = input_sha256
    out["universe_manifest_seed"] = registry_build_seed
    out["universe_manifest_run_timestamp_utc"] = run_timestamp_utc
    out["holdout_status"] = "sealed_not_used"
    out["target_track"] = "HS_LS"
    out["margin_track_status_note"] = "BHW/GHL fields carried when available but not part of first-pass HS/LS model scope."
    out["predictive_claim_status"] = "descriptor_inventory_only_requires_fold_clean_oof_validation"
    return out

A = stamp_manifest(A, "A", "Tier A engine candidates", "strict_first_pass_baseline", "engine_candidate_pool == True AND coverage_tier_normalized == 'Tier A'")
B = stamp_manifest(B, "B", "Tier A+B+C engine candidates", "expanded_first_pass_increment", "engine_candidate_pool == True AND coverage_tier_normalized in {'Tier A','Tier B','Tier C'}")
C = stamp_manifest(C, "C", "Representation-development candidates", "not_first_pass_model_input", "representation_development_pool == True")

strength_order = {"A_rich_clean": 1, "B_partial_clean": 2, "C_light_clean": 3}
for d in [A, B, C]:
    d["candidate_strength_rank"] = d["engine_candidate_strength"].map(strength_order).fillna(99).astype(int)

sort_cols = ["modeling_universe_id", "candidate_strength_rank", "coverage_tier_normalized", "system_pair", "origin", "origin_frame", "target_body", "target_frame", "feature_id"]
A = A.sort_values(sort_cols).reset_index(drop=True)
B = B.sort_values(sort_cols).reset_index(drop=True)
C = C.sort_values(sort_cols).reset_index(drop=True)

preferred_cols = [
    "modeling_universe_id", "modeling_universe_name", "modeling_role", "modeling_universe_rule",
    "feature_id", "source_file", "system_pair", "origin", "origin_frame", "target_body",
    "target_frame", "same_or_cross", "origin_category", "coverage_tier_normalized",
    "coverage_validity_class", "characterization_status", "engine_candidate_strength",
    "candidate_strength_rank", "representation_development_reason", "primary_modeling_track",
    "analysis_layers_present", "has_paper1_data", "has_phase1p5_data", "has_fsa_data",
    "has_hlon_data", "has_step2c_data", "has_operating_point_data", "has_priority_data",
    "has_phase3c_data", "has_HS_fields", "has_LS_fields", "has_BHW_fields", "has_GHL_fields",
    "margin_track_status", "paper1_HS_peak_degree", "paper1_LS_peak_degree", "paper1_HS_peak_lift",
    "paper1_LS_peak_lift", "paper1_HS_support", "paper1_LS_support", "hlon_HS_peak_degree",
    "hlon_LS_peak_degree", "hlon_HS_peak_lift", "hlon_LS_peak_lift", "hlon_HS_support",
    "hlon_LS_support", "step2c_HS_peak_degree", "step2c_LS_peak_degree", "step2c_HS_peak_lift",
    "step2c_LS_peak_lift", "operating_HS_peak_degree", "operating_LS_peak_degree",
    "operating_HS_peak_lift", "operating_LS_peak_lift", "fsa_operational_class",
    "fsa_resolution_mode", "fsa_recommended_resolution", "fsa_velocity", "fsa_drift",
    "descriptor_evidence_only", "requires_oof_validation_before_candidate_selection",
    "safe_for_direct_predictive_claim", "holdout_status", "target_track", "margin_track_status_note",
    "predictive_claim_status", "universe_manifest_version", "universe_manifest_input_sha256",
    "universe_manifest_seed", "universe_manifest_run_timestamp_utc",
]

def compact(df):
    return df[[c for c in preferred_cols if c in df.columns]].copy()

A_out, B_out, C_out = compact(A), compact(B), compact(C)

A_set, B_set, C_set = set(A_out["feature_id"]), set(B_out["feature_id"]), set(C_out["feature_id"])
qa_rows = [
    {"check": "Universe A rows", "expected": 345, "observed": len(A_out), "pass": len(A_out) == 345},
    {"check": "Universe B rows", "expected": 423, "observed": len(B_out), "pass": len(B_out) == 423},
    {"check": "Universe C rows", "expected": 510, "observed": len(C_out), "pass": len(C_out) == 510},
    {"check": "Universe A unique feature_id", "expected": len(A_out), "observed": A_out["feature_id"].nunique(), "pass": A_out["feature_id"].nunique() == len(A_out)},
    {"check": "Universe B unique feature_id", "expected": len(B_out), "observed": B_out["feature_id"].nunique(), "pass": B_out["feature_id"].nunique() == len(B_out)},
    {"check": "Universe C unique feature_id", "expected": len(C_out), "observed": C_out["feature_id"].nunique(), "pass": C_out["feature_id"].nunique() == len(C_out)},
    {"check": "A subset B", "expected": True, "observed": A_set.issubset(B_set), "pass": A_set.issubset(B_set)},
    {"check": "B disjoint C", "expected": True, "observed": B_set.isdisjoint(C_set), "pass": B_set.isdisjoint(C_set)},
    {"check": "B plus C characterized universe", "expected": 933, "observed": len(B_set) + len(C_set), "pass": (len(B_set) + len(C_set)) == 933},
    {"check": "Universe B Tier A", "expected": 345, "observed": int((B_out["coverage_tier_normalized"] == "Tier A").sum()), "pass": int((B_out["coverage_tier_normalized"] == "Tier A").sum()) == 345},
    {"check": "Universe B Tier B", "expected": 51, "observed": int((B_out["coverage_tier_normalized"] == "Tier B").sum()), "pass": int((B_out["coverage_tier_normalized"] == "Tier B").sum()) == 51},
    {"check": "Universe B Tier C", "expected": 27, "observed": int((B_out["coverage_tier_normalized"] == "Tier C").sum()), "pass": int((B_out["coverage_tier_normalized"] == "Tier C").sum()) == 27},
]

for universe_name, table in [("A", A_out), ("B", B_out), ("C", C_out)]:
    safe_claims = int(table["safe_for_direct_predictive_claim"].astype(bool).sum())
    qa_rows.append({"check": f"Universe {universe_name} direct predictive claims", "expected": 0, "observed": safe_claims, "pass": safe_claims == 0})

qa = pd.DataFrame(qa_rows)
if not qa["pass"].all():
    raise AssertionError("v1.7 QA failed:\n" + qa.to_string(index=False))

A_out.to_csv(OUT_A, index=False)
B_out.to_csv(OUT_B, index=False)
C_out.to_csv(OUT_C, index=False)
qa.to_csv(OUT_QA, index=False)

def count_table(df, cols, name):
    t = df.groupby(cols, dropna=False).size().reset_index(name="n_features").sort_values("n_features", ascending=False)
    t.insert(0, "table", name)
    return t

B_tier_by_strength = pd.crosstab(B_out["coverage_tier_normalized"], B_out["engine_candidate_strength"], margins=True)
C_reason = count_table(C_out, ["representation_development_reason"], "C_reason")

lines = []
lines.append("=" * 90)
lines.append("HS/LS MODELING UNIVERSE MANIFESTS v1.7 COMPLETE")
lines.append("=" * 90)
lines.append(f"Input: {IN}")
lines.append(f"Input SHA-256: {input_sha256}")
lines.append(f"Run timestamp UTC: {run_timestamp_utc}")
lines.append("")
lines.append("UNIVERSE DEFINITIONS")
lines.append("A: Tier A only, engine_candidate_pool == True; strict first-pass baseline.")
lines.append("B: Tier A+B+C, engine_candidate_pool == True; expanded nested increment over A.")
lines.append("C: representation_development_pool == True; not first-pass model input.")
lines.append("")
lines.append("ROWS")
lines.append(f"Universe A: {len(A_out)}")
lines.append(f"Universe B: {len(B_out)}")
lines.append(f"Universe C: {len(C_out)}")
lines.append("")
lines.append("QA")
lines.append(qa.to_string(index=False))
lines.append("")
lines.append("UNIVERSE B TIER × STRENGTH")
lines.append(B_tier_by_strength.to_string())
lines.append("")
lines.append("UNIVERSE C REASON")
lines.append(C_reason.to_string(index=False))
lines.append("")
lines.append("OUTPUTS")
lines.append(str(OUT_A))
lines.append(str(OUT_B))
lines.append(str(OUT_C))
lines.append(str(OUT_QA))
lines.append(str(OUT_TXT))
lines.append("=" * 90)

OUT_TXT.write_text("\n".join(lines))
print("\n".join(lines))
