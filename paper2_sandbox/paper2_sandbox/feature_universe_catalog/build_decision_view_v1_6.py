# MASTER ASPECT FEATURE DECISION VIEW v1.6
from pathlib import Path
import pandas as pd
import numpy as np
import re
import hashlib
from datetime import datetime, timezone

SANDBOX = Path("/content/drive/MyDrive/OMNI_PROJECT/paper2_sandbox")
IN = SANDBOX / "MASTER_ASPECT_FEATURE_CHARACTERIZATION_REGISTRY_v1_5.csv"
OUT = SANDBOX / "MASTER_ASPECT_FEATURE_DECISION_VIEW_v1_6.csv"
OUT_QA = SANDBOX / "MASTER_ASPECT_FEATURE_DECISION_VIEW_QA_v1_6.csv"
OUT_TXT = SANDBOX / "MASTER_ASPECT_FEATURE_DECISION_VIEW_SUMMARY_v1_6.txt"

EXPECTED_LAYER_TOTALS = {
    "has_paper1_data": 741, "has_phase1p5_data": 6, "has_fsa_data": 241,
    "has_hlon_data": 192, "has_step2c_data": 209, "has_operating_point_data": 209,
    "has_priority_data": 18, "has_phase3c_data": 192,
}

def sha256_file(path, block_size=1024 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            h.update(block)
    return h.hexdigest()

def find_best_col(columns, include_terms, exclude_terms=None):
    exclude_terms = exclude_terms or []
    candidates = []
    for c in columns:
        lc = c.lower()
        if all(term.lower() in lc for term in include_terms) and not any(term.lower() in lc for term in exclude_terms):
            candidates.append(c)
    return sorted(candidates, key=lambda x: (len(x), x))[0] if candidates else ""

def pick(row, col):
    return row[col] if col and col in row.index else np.nan

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
df = pd.read_csv(IN, low_memory=False)
cols = list(df.columns)

paper1_hs_peak_degree_col = find_best_col(cols, ["paper1", "HS", "peak", "degree"])
paper1_ls_peak_degree_col = find_best_col(cols, ["paper1", "LS", "peak", "degree"])
paper1_hs_peak_lift_col = find_best_col(cols, ["paper1", "HS", "peak", "lift"])
paper1_ls_peak_lift_col = find_best_col(cols, ["paper1", "LS", "peak", "lift"])
paper1_hs_support_col = find_best_col(cols, ["paper1", "HS", "support"])
paper1_ls_support_col = find_best_col(cols, ["paper1", "LS", "support"])

hlon_hs_peak_degree_col = find_best_col(cols, ["hlon", "HS", "peak", "degree"])
hlon_ls_peak_degree_col = find_best_col(cols, ["hlon", "LS", "peak", "degree"])
hlon_bhw_peak_degree_col = find_best_col(cols, ["hlon", "BHW", "peak", "degree"])
hlon_ghl_peak_degree_col = find_best_col(cols, ["hlon", "GHL", "peak", "degree"])
hlon_hs_peak_lift_col = find_best_col(cols, ["hlon", "HS", "peak", "lift"])
hlon_ls_peak_lift_col = find_best_col(cols, ["hlon", "LS", "peak", "lift"])
hlon_bhw_peak_lift_col = find_best_col(cols, ["hlon", "BHW", "peak", "lift"])
hlon_ghl_peak_lift_col = find_best_col(cols, ["hlon", "GHL", "peak", "lift"])
hlon_hs_support_col = find_best_col(cols, ["hlon", "HS", "support"])
hlon_ls_support_col = find_best_col(cols, ["hlon", "LS", "support"])
hlon_bhw_support_col = find_best_col(cols, ["hlon", "BHW", "support"])
hlon_ghl_support_col = find_best_col(cols, ["hlon", "GHL", "support"])

fsa_operational_class_col = find_best_col(cols, ["fsa", "operational", "class"])
fsa_resolution_mode_col = find_best_col(cols, ["fsa", "resolution", "mode"])
fsa_recommended_resolution_col = find_best_col(cols, ["fsa", "recommended", "resolution"])
fsa_velocity_col = find_best_col(cols, ["fsa", "velocity"])
fsa_drift_col = find_best_col(cols, ["fsa", "drift"])

step2c_hs_peak_lift_col = find_best_col(cols, ["step2c", "HS", "peak", "lift"])
step2c_ls_peak_lift_col = find_best_col(cols, ["step2c", "LS", "peak", "lift"])
step2c_hs_peak_degree_col = find_best_col(cols, ["step2c", "HS", "peak", "degree"])
step2c_ls_peak_degree_col = find_best_col(cols, ["step2c", "LS", "peak", "degree"])

op_hs_peak_lift_col = find_best_col(cols, ["operating_point", "HS", "peak", "lift"])
op_ls_peak_lift_col = find_best_col(cols, ["operating_point", "LS", "peak", "lift"])
op_hs_peak_degree_col = find_best_col(cols, ["operating_point", "HS", "peak", "degree"])
op_ls_peak_degree_col = find_best_col(cols, ["operating_point", "LS", "peak", "degree"])

phase3c_reliable_high_col = find_best_col(cols, ["phase3c", "reliable", "high"])
phase3c_reliable_low_col = find_best_col(cols, ["phase3c", "reliable", "low"])
phase3c_origin_class_col = find_best_col(cols, ["phase3c", "origin", "class"])

RESOLVED = {
    "paper1_HS_peak_lift": paper1_hs_peak_lift_col,
    "paper1_LS_peak_lift": paper1_ls_peak_lift_col,
    "paper1_HS_peak_degree": paper1_hs_peak_degree_col,
    "paper1_LS_peak_degree": paper1_ls_peak_degree_col,
    "hlon_HS_peak_lift": hlon_hs_peak_lift_col,
    "hlon_LS_peak_lift": hlon_ls_peak_lift_col,
    "step2c_HS_peak_lift": step2c_hs_peak_lift_col,
    "operating_HS_peak_lift": op_hs_peak_lift_col,
    "fsa_operational_class": fsa_operational_class_col,
    "phase3c_origin_class": phase3c_origin_class_col,
}
print("COLUMN RESOLUTION MAP (term-set -> v1.5 column; '' = NOT FOUND):")
for k, v in RESOLVED.items():
    print(f"  {k:24s} -> {v!r}")

CRITICAL = ["paper1_HS_peak_lift", "paper1_LS_peak_lift", "paper1_HS_peak_degree", "paper1_LS_peak_degree"]
unresolved = [k for k in CRITICAL if not RESOLVED[k]]
assert not unresolved, f"find_best_col missed core HS/LS evidence {unresolved}"

view = pd.DataFrame()
for c in [
    "feature_id", "source_file", "system_pair", "origin", "origin_frame", "target_body",
    "target_frame", "same_or_cross", "origin_category", "coverage_tier",
    "coverage_tier_normalized", "coverage_validity_class", "analysis_scope_flag",
    "characterization_status", "descriptor_candidate_status", "analysis_layers_present",
    "outcome_pole_field_count"
]:
    view[c] = df[c]

for c in [
    "has_paper1_data", "has_phase1p5_data", "has_fsa_data", "has_hlon_data",
    "has_step2c_data", "has_operating_point_data", "has_priority_data", "has_phase3c_data",
    "has_HS_fields", "has_LS_fields", "has_BHW_fields", "has_GHL_fields"
]:
    view[c] = df[c].map(bool_clean)

view["paper1_HS_peak_degree"] = df.apply(lambda r: pick(r, paper1_hs_peak_degree_col), axis=1)
view["paper1_LS_peak_degree"] = df.apply(lambda r: pick(r, paper1_ls_peak_degree_col), axis=1)
view["paper1_HS_peak_lift"] = df.apply(lambda r: pick(r, paper1_hs_peak_lift_col), axis=1)
view["paper1_LS_peak_lift"] = df.apply(lambda r: pick(r, paper1_ls_peak_lift_col), axis=1)
view["paper1_HS_support"] = df.apply(lambda r: pick(r, paper1_hs_support_col), axis=1)
view["paper1_LS_support"] = df.apply(lambda r: pick(r, paper1_ls_support_col), axis=1)

view["hlon_HS_peak_degree"] = df.apply(lambda r: pick(r, hlon_hs_peak_degree_col), axis=1)
view["hlon_LS_peak_degree"] = df.apply(lambda r: pick(r, hlon_ls_peak_degree_col), axis=1)
view["hlon_BHW_peak_degree"] = df.apply(lambda r: pick(r, hlon_bhw_peak_degree_col), axis=1)
view["hlon_GHL_peak_degree"] = df.apply(lambda r: pick(r, hlon_ghl_peak_degree_col), axis=1)
view["hlon_HS_peak_lift"] = df.apply(lambda r: pick(r, hlon_hs_peak_lift_col), axis=1)
view["hlon_LS_peak_lift"] = df.apply(lambda r: pick(r, hlon_ls_peak_lift_col), axis=1)
view["hlon_BHW_peak_lift"] = df.apply(lambda r: pick(r, hlon_bhw_peak_lift_col), axis=1)
view["hlon_GHL_peak_lift"] = df.apply(lambda r: pick(r, hlon_ghl_peak_lift_col), axis=1)
view["hlon_HS_support"] = df.apply(lambda r: pick(r, hlon_hs_support_col), axis=1)
view["hlon_LS_support"] = df.apply(lambda r: pick(r, hlon_ls_support_col), axis=1)
view["hlon_BHW_support"] = df.apply(lambda r: pick(r, hlon_bhw_support_col), axis=1)
view["hlon_GHL_support"] = df.apply(lambda r: pick(r, hlon_ghl_support_col), axis=1)

view["fsa_operational_class"] = df.apply(lambda r: pick(r, fsa_operational_class_col), axis=1)
view["fsa_resolution_mode"] = df.apply(lambda r: pick(r, fsa_resolution_mode_col), axis=1)
view["fsa_recommended_resolution"] = df.apply(lambda r: pick(r, fsa_recommended_resolution_col), axis=1)
view["fsa_velocity"] = df.apply(lambda r: pick(r, fsa_velocity_col), axis=1)
view["fsa_drift"] = df.apply(lambda r: pick(r, fsa_drift_col), axis=1)

view["step2c_HS_peak_degree"] = df.apply(lambda r: pick(r, step2c_hs_peak_degree_col), axis=1)
view["step2c_LS_peak_degree"] = df.apply(lambda r: pick(r, step2c_ls_peak_degree_col), axis=1)
view["step2c_HS_peak_lift"] = df.apply(lambda r: pick(r, step2c_hs_peak_lift_col), axis=1)
view["step2c_LS_peak_lift"] = df.apply(lambda r: pick(r, step2c_ls_peak_lift_col), axis=1)

view["operating_HS_peak_degree"] = df.apply(lambda r: pick(r, op_hs_peak_degree_col), axis=1)
view["operating_LS_peak_degree"] = df.apply(lambda r: pick(r, op_ls_peak_degree_col), axis=1)
view["operating_HS_peak_lift"] = df.apply(lambda r: pick(r, op_hs_peak_lift_col), axis=1)
view["operating_LS_peak_lift"] = df.apply(lambda r: pick(r, op_ls_peak_lift_col), axis=1)

view["phase3c_origin_class"] = df.apply(lambda r: pick(r, phase3c_origin_class_col), axis=1)
view["phase3c_reliable_high"] = df.apply(lambda r: pick(r, phase3c_reliable_high_col), axis=1)
view["phase3c_reliable_low"] = df.apply(lambda r: pick(r, phase3c_reliable_low_col), axis=1)

nn = view.loc[view["has_paper1_data"], "paper1_HS_peak_lift"].notna().sum()
assert nn > 0, "paper1_HS_peak_lift all-NaN on paper1 rows"
print(f"paper1_HS_peak_lift populated on {nn}/{int(view['has_paper1_data'].sum())} paper1 rows")

clean_classes = {"coverage_clean", "coverage_clean_or_rotationally_supported"}
characterized_classes = {"lightly_characterized", "partially_characterized", "richly_characterized"}

view["is_characterized"] = view["characterization_status"].isin(characterized_classes)
view["is_coverage_clean_for_engine"] = view["coverage_validity_class"].isin(clean_classes)
view["engine_candidate_pool"] = view["is_characterized"] & view["is_coverage_clean_for_engine"] & (view["analysis_scope_flag"] == "in_scope")
view["engine_candidate_strength"] = np.select(
    [
        view["engine_candidate_pool"] & (view["characterization_status"] == "richly_characterized"),
        view["engine_candidate_pool"] & (view["characterization_status"] == "partially_characterized"),
        view["engine_candidate_pool"] & (view["characterization_status"] == "lightly_characterized"),
    ],
    ["A_rich_clean", "B_partial_clean", "C_light_clean"],
    default=""
)
view["representation_development_pool"] = view["is_characterized"] & (~view["is_coverage_clean_for_engine"]) & (view["analysis_scope_flag"] == "in_scope")
view["representation_development_reason"] = np.where(view["representation_development_pool"], view["coverage_validity_class"], "")
view["margin_track_status"] = np.where(view["has_BHW_fields"] | view["has_GHL_fields"], "margin_BHW_GHL_available_but_paused", "margin_BHW_GHL_not_available")
view["primary_modeling_track"] = np.where(
    view["engine_candidate_pool"], "HS_LS_first_pass_candidate",
    np.where(view["representation_development_pool"], "representation_development_not_first_pass",
             np.where(view["analysis_scope_flag"] != "in_scope", "excluded_not_current_scope", "not_yet_characterized"))
)
view["descriptor_evidence_only"] = True
view["requires_oof_validation_before_candidate_selection"] = True
view["safe_for_direct_predictive_claim"] = False
view["registry_build_seed"] = registry_build_seed
view["registry_input_sha256"] = input_sha256
view["registry_run_timestamp_utc"] = run_timestamp_utc

qa_rows = [
    {"check": "rows_match_input", "expected": len(df), "observed": len(view), "pass": len(df) == len(view)},
    {"check": "unique_feature_id", "expected": len(view), "observed": view["feature_id"].nunique(), "pass": view["feature_id"].nunique() == len(view)},
]
for col, exp in EXPECTED_LAYER_TOTALS.items():
    obs = int(view[col].sum())
    qa_rows.append({"check": f"layer_total::{col}", "expected": exp, "observed": obs, "pass": obs == exp})

qa_rows += [
    {"check": "engine_candidate_pool", "expected": 423, "observed": int(view["engine_candidate_pool"].sum()), "pass": int(view["engine_candidate_pool"].sum()) == 423},
    {"check": "A_rich_clean", "expected": 102, "observed": int((view["engine_candidate_strength"] == "A_rich_clean").sum()), "pass": int((view["engine_candidate_strength"] == "A_rich_clean").sum()) == 102},
    {"check": "B_partial_clean", "expected": 91, "observed": int((view["engine_candidate_strength"] == "B_partial_clean").sum()), "pass": int((view["engine_candidate_strength"] == "B_partial_clean").sum()) == 91},
    {"check": "C_light_clean", "expected": 230, "observed": int((view["engine_candidate_strength"] == "C_light_clean").sum()), "pass": int((view["engine_candidate_strength"] == "C_light_clean").sum()) == 230},
    {"check": "representation_development_pool", "expected": 510, "observed": int(view["representation_development_pool"].sum()), "pass": int(view["representation_development_pool"].sum()) == 510},
    {"check": "paper1_HS_peak_lift_populated", "expected": ">0", "observed": int(nn), "pass": int(nn) > 0},
]
qa = pd.DataFrame(qa_rows)
if not qa["pass"].all():
    raise AssertionError("v1.6 QA failed:\n" + qa.to_string(index=False))

view.to_csv(OUT, index=False)
qa.to_csv(OUT_QA, index=False)

def count_table(cols, name):
    out = view.groupby(cols, dropna=False).size().reset_index(name="n_features").sort_values("n_features", ascending=False)
    out.insert(0, "table", name)
    return out

tables = {
    "engine_candidate_strength": count_table(["engine_candidate_strength"], "engine_candidate_strength"),
    "primary_modeling_track": count_table(["primary_modeling_track"], "primary_modeling_track"),
    "representation_dev_reason": count_table(["representation_development_reason"], "representation_development_reason"),
    "margin_track_status": count_table(["margin_track_status"], "margin_track_status"),
}

lines = []
lines.append("=" * 90)
lines.append("MASTER ASPECT FEATURE DECISION VIEW v1.6 COMPLETE")
lines.append("=" * 90)
lines.append(f"Input: {IN}")
lines.append(f"Input SHA-256: {input_sha256}")
lines.append(f"Registry build seed: {registry_build_seed}")
lines.append(f"Run timestamp UTC: {run_timestamp_utc}")
lines.append(f"Rows: {len(view)}")
lines.append(f"Columns: {len(view.columns)}")
lines.append("")
lines.append("COLUMN RESOLUTION MAP")
for k, v in RESOLVED.items():
    lines.append(f"{k:24s} -> {v!r}")
lines.append("")
lines.append("QA")
lines.append(qa.to_string(index=False))
lines.append("")
lines.append("ENGINE CANDIDATE STRENGTH")
lines.append(tables["engine_candidate_strength"].to_string(index=False))
lines.append("")
lines.append("PRIMARY MODELING TRACK")
lines.append(tables["primary_modeling_track"].to_string(index=False))
lines.append("")
lines.append("REPRESENTATION DEVELOPMENT REASON")
lines.append(tables["representation_dev_reason"].to_string(index=False))
lines.append("")
lines.append("MARGIN TRACK STATUS")
lines.append(tables["margin_track_status"].to_string(index=False))
lines.append("")
lines.append("OUTPUTS")
lines.append(str(OUT))
lines.append(str(OUT_QA))
lines.append(str(OUT_TXT))
lines.append("=" * 90)

OUT_TXT.write_text("\n".join(lines))
print("\n".join(lines))
