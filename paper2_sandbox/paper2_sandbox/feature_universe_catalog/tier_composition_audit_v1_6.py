from pathlib import Path
import pandas as pd

SANDBOX = Path("/content/drive/MyDrive/OMNI_PROJECT/paper2_sandbox")
REG = SANDBOX / "MASTER_ASPECT_FEATURE_DECISION_VIEW_v1_6.csv"

v = pd.read_csv(REG, low_memory=False)
pool = v[v["engine_candidate_pool"].astype(str).str.lower().isin(["true", "1", "yes"])]

print("ENGINE POOL (n=423) BY COVERAGE TIER:")
print(pool["coverage_tier_normalized"].value_counts(dropna=False).to_string())
print()
print(pd.crosstab(pool["coverage_tier_normalized"], pool["engine_candidate_strength"], margins=True).to_string())
