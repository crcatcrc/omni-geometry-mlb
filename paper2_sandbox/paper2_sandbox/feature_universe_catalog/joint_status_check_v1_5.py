from pathlib import Path
import pandas as pd

SANDBOX = Path("/content/drive/MyDrive/OMNI_PROJECT/paper2_sandbox")
REG = SANDBOX / "MASTER_ASPECT_FEATURE_CHARACTERIZATION_REGISTRY_v1_5.csv"

df = pd.read_csv(REG, low_memory=False)

ct = pd.crosstab(
    df["characterization_status"],
    df["coverage_validity_class"],
    margins=True
)

print("=" * 90)
print("CHARACTERIZATION STATUS × COVERAGE VALIDITY CLASS")
print("=" * 90)
print(ct.to_string())

clean = {"coverage_clean", "coverage_clean_or_rotationally_supported"}
chars = {"richly_characterized", "partially_characterized", "lightly_characterized"}

pool = df[
    df["characterization_status"].isin(chars)
    & df["coverage_validity_class"].isin(clean)
].copy()

print()
print("=" * 90)
print("CLEAN CHARACTERIZED DESCRIPTOR POOL")
print("=" * 90)
print("characterized & coverage-clean :", len(pool))
print("by characterization_status:", pool["characterization_status"].value_counts().to_dict())
print("by coverage_validity_class:", pool["coverage_validity_class"].value_counts().to_dict())
print("by descriptor_candidate_status:", pool["descriptor_candidate_status"].value_counts().to_dict())

print()
print("=" * 90)
print("RICHLY CHARACTERIZED BUT NOT COVERAGE-CLEAN")
print("=" * 90)

rich_not_clean = df[
    (df["characterization_status"] == "richly_characterized")
    & (~df["coverage_validity_class"].isin(clean))
].copy()

print("rich_not_clean:", len(rich_not_clean))
print("by coverage_validity_class:", rich_not_clean["coverage_validity_class"].value_counts().to_dict())
print("by coverage_tier_normalized:", rich_not_clean["coverage_tier_normalized"].value_counts(dropna=False).to_dict())
