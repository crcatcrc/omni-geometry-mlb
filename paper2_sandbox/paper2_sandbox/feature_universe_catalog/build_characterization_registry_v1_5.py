# MASTER ASPECT FEATURE CHARACTERIZATION REGISTRY v1.5
from pathlib import Path
import pandas as pd
import numpy as np
import re

SANDBOX = Path("/content/drive/MyDrive/OMNI_PROJECT/paper2_sandbox")
IN = SANDBOX / "MASTER_ASPECT_FEATURE_ANALYSIS_REGISTRY_v1_3.csv"
OUT = SANDBOX / "MASTER_ASPECT_FEATURE_CHARACTERIZATION_REGISTRY_v1_5.csv"
OUT_QA = SANDBOX / "MASTER_ASPECT_FEATURE_CHARACTERIZATION_REGISTRY_QA_v1_5.csv"
OUT_TXT = SANDBOX / "MASTER_ASPECT_FEATURE_CHARACTERIZATION_REGISTRY_SUMMARY_v1_5.txt"

EXPECTED_LAYER_TOTALS = {
    "has_paper1_data": 741,
    "has_phase1p5_data": 6,
    "has_fsa_data": 241,
    "has_hlon_data": 192,
    "has_step2c_data": 209,
    "has_operating_point_data": 209,
    "has_priority_data": 18,
    "has_phase3c_data": 192,
}

df = pd.read_csv(IN, low_memory=False)

REQUIRED = [
    "feature_id", "analysis_scope_flag", "coverage_tier", "origin_frame",
    "target_frame", "system_pair", "origin", "target_body"
]
missing = [c for c in REQUIRED if c not in df.columns]
assert not missing, f"v1.3 missing columns {missing}; classifiers would mislabel silently."

for c in ["analysis_scope_flag", "coverage_tier", "origin_frame", "target_frame", "system_pair"]:
    df[c] = df[c].astype(str).str.strip()

scope_counts = df["analysis_scope_flag"].value_counts(dropna=False).to_dict()
tier_counts = df["coverage_tier"].value_counts(dropna=False).to_dict()

print("scope values :", scope_counts)
print("tier values  :", tier_counts)

n_in_scope = int((df["analysis_scope_flag"] == "in_scope").sum())
assert 2000 <= n_in_scope <= 2494, f"in_scope={n_in_scope}; expected approximately 2253."

layer_flags = list(EXPECTED_LAYER_TOTALS.keys())
for col in layer_flags:
    if col not in df.columns:
        df[col] = False
    df[col] = df[col].fillna(False).astype(bool)

df["analysis_layers_present"] = df[layer_flags].sum(axis=1)

qa_rows = []
for col, expected in EXPECTED_LAYER_TOTALS.items():
    observed = int(df[col].sum())
    qa_rows.append({"check": f"checksum_{col}", "expected": expected, "observed": observed, "pass": observed == expected})

failed = [r for r in qa_rows if not r["pass"]]
if failed:
    raise AssertionError(f"Layer checksum failure: {failed}")

def clean_token(x):
    x = str(x).strip()
    if x.lower() in {"nan", "none", ""}:
        return ""
    return x

def normalized_tier(tier):
    t = clean_token(tier)
    tl = t.lower().replace("_", " ").replace("-", " ").strip()
    tl = re.sub(r"\s+", " ", tl)

    if tl in {"tier a", "a"}:
        return "Tier A"
    if tl in {"tier b", "b"}:
        return "Tier B"
    if tl in {"tier c", "c"}:
        return "Tier C"
    if tl in {"constrained motion", "constrained", "inner constrained", "constrained inner"}:
        return "Constrained-motion"
    if tl in {"sparse coverage", "sparse", "outer sparse", "sparse outer"}:
        return "Sparse-coverage"
    if tl in {"earth solar locked", "earth/solar locked", "earth", "ear", "solar locked"}:
        return "Earth/solar-locked"
    if tl in {"part of fortune", "pof", "pofd", "pfff", "pfdn"}:
        return "Part of Fortune"
    return t

df["coverage_tier_normalized"] = df["coverage_tier"].map(normalized_tier)

def coverage_validity(row):
    tier = clean_token(row.get("coverage_tier_normalized", ""))
    origin_frame = clean_token(row.get("origin_frame", ""))
    target_frame = clean_token(row.get("target_frame", ""))
    scope = clean_token(row.get("analysis_scope_flag", ""))

    if scope != "in_scope":
        return "excluded_not_analyzed"
    if tier in {"Constrained-motion", "Sparse-coverage", "Earth/solar-locked", "Part of Fortune"}:
        return "quarantine_or_special_handling"
    if tier in {"Tier B", "Tier C"}:
        if origin_frame == "G-AZ" or target_frame == "G-AZ":
            return "coverage_clean_or_rotationally_supported"
        return "coverage_conditional"
    if tier == "Tier A":
        return "coverage_clean"
    return "coverage_unclassified"

df["coverage_validity_class"] = df.apply(coverage_validity, axis=1)
n_unclassified = int((df["coverage_validity_class"] == "coverage_unclassified").sum())
assert n_unclassified < 0.5 * len(df), f"{n_unclassified}/{len(df)} unclassified."

def characterization_status(row):
    if clean_token(row.get("analysis_scope_flag", "")) != "in_scope":
        return "excluded_not_analyzed"
    n = int(row["analysis_layers_present"])
    if n == 0:
        return "unanalyzed"
    if n == 1:
        return "lightly_characterized"
    if n in {2, 3}:
        return "partially_characterized"
    if n >= 4:
        return "richly_characterized"
    return "unknown"

df["characterization_status"] = df.apply(characterization_status, axis=1)

pole_prefixes = ["HS", "LS", "BHW", "GHL"]
def pole_columns_for(pole):
    patterns = [f"_{pole}_", f"{pole}_", f"_{pole}"]
    return [c for c in df.columns if any(p in c for p in patterns)]

for pole in pole_prefixes:
    pole_cols = pole_columns_for(pole)
    df[f"has_{pole}_fields"] = df[pole_cols].notna().any(axis=1) if pole_cols else False

df["outcome_pole_field_count"] = df[[f"has_{p}_fields" for p in pole_prefixes]].sum(axis=1)

metric_terms = [
    "peak", "lift", "degree", "count", "support", "lock",
    "persistent", "anchor", "fragile", "operational", "velocity", "drift", "resolution"
]
metric_cols = [c for c in df.columns if any(term in c.lower() for term in metric_terms) and not c.startswith("has_")]
qa_rows.append({"check": "metric_columns_present", "expected": ">0", "observed": len(metric_cols), "pass": len(metric_cols) > 0})
qa_rows.append({"check": "rows_with_any_outcome_pole_fields", "expected": ">0", "observed": int((df["outcome_pole_field_count"] > 0).sum()), "pass": int((df["outcome_pole_field_count"] > 0).sum()) > 0})
if len(metric_cols) == 0:
    raise AssertionError("No metric columns detected.")

df["descriptor_evidence_only"] = True
df["requires_oof_validation_before_candidate_selection"] = True
df["safe_for_direct_predictive_claim"] = False

def descriptive_candidate_status(row):
    if row["characterization_status"] == "excluded_not_analyzed":
        return "excluded_from_current_analysis_scope"
    if row["characterization_status"] == "unanalyzed":
        return "not_yet_characterized"
    if row["coverage_validity_class"] in {"quarantine_or_special_handling", "coverage_conditional", "coverage_unclassified"}:
        return "characterized_but_requires_coverage_handling"
    if row["characterization_status"] == "richly_characterized":
        return "well_characterized_descriptor_candidate"
    if row["characterization_status"] == "partially_characterized":
        return "partially_characterized_descriptor_candidate"
    return "lightly_characterized_descriptor_candidate"

df["descriptor_candidate_status"] = df.apply(descriptive_candidate_status, axis=1)

def count_table(cols, name):
    out = df.groupby(cols, dropna=False).size().reset_index(name="n_features").sort_values("n_features", ascending=False)
    out.insert(0, "table", name)
    return out

summary_tables = {
    "characterization_status": count_table(["characterization_status"], "characterization_status"),
    "coverage_validity_class": count_table(["coverage_validity_class"], "coverage_validity_class"),
    "descriptor_candidate_status": count_table(["descriptor_candidate_status"], "descriptor_candidate_status"),
    "pole_field_count": count_table(["outcome_pole_field_count"], "pole_field_count"),
}

df.to_csv(OUT, index=False)
qa = pd.DataFrame(qa_rows)
qa.to_csv(OUT_QA, index=False)

lines = []
lines.append("=" * 90)
lines.append("MASTER ASPECT FEATURE CHARACTERIZATION REGISTRY v1.5 COMPLETE")
lines.append("=" * 90)
lines.append(f"Input: {IN}")
lines.append(f"Rows: {len(df)}")
lines.append(f"Columns: {len(df.columns)}")
lines.append("")
lines.append("SCOPE VALUES")
lines.append(str(scope_counts))
lines.append("")
lines.append("TIER VALUES")
lines.append(str(tier_counts))
lines.append("")
lines.append("CHECKSUMS / QA")
lines.append(qa.to_string(index=False))
lines.append("")
lines.append("CHARACTERIZATION STATUS")
lines.append(summary_tables["characterization_status"].to_string(index=False))
lines.append("")
lines.append("COVERAGE VALIDITY CLASS")
lines.append(summary_tables["coverage_validity_class"].to_string(index=False))
lines.append("")
lines.append("DESCRIPTOR CANDIDATE STATUS")
lines.append(summary_tables["descriptor_candidate_status"].to_string(index=False))
lines.append("")
lines.append("OUTCOME-POLE FIELD COUNT")
lines.append(summary_tables["pole_field_count"].to_string(index=False))
lines.append("")
lines.append("OUTPUTS")
lines.append(str(OUT))
lines.append(str(OUT_QA))
lines.append(str(OUT_TXT))
lines.append("=" * 90)

OUT_TXT.write_text("\n".join(lines))
print("\n".join(lines))
