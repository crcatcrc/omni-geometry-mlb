# OMNI Paper 2 Sandbox — Milestone Manifest
## Tier 1 Feature Separation Audit + Operational-Scale Registry

**Date:** 2026-05-28  **Status:** LOCKED (exploratory; Charter §1)

## What this milestone established
The audit measured, per feature, the operational angular scale at which each
aspect feature varies between near-concurrent same-slate games; the registry
codifies that into feature-engineering rules. Organizing relation:

    same-slate discriminability  =  within-slate spread  ×  local lift gradient

This milestone delivers the **spread** half. 241 features classified:
157 same-slate-discriminator, 52 marginal, 32 slow-contextual. Operational
classes are **provisional** working labels (heuristic thresholds; not yet
linked to lift behaviour or predictive usefulness).

## Provenance anchors (SHA-256)
- Audit master `feature_separation_audit_master.csv`
  `e5a6bad6c54a5460c25674dd0a9aa61a5c3bd3c6c48c054568829262744ccdd1`
- Registry `operational_scale_registry_v1_0.csv`
  `68319a2ef1ba1556653e7e4094959cd25704482c389fd276c24faaf305c1891a`
- Generating cell: `tier1_feature_separation_audit.py` v2.1

Companion files (dt_bins, drift, summary, class_rollup, registry meta) are
derived deterministically from the master by the versioned cell and the
SHA-guarded registry builder; their integrity is guaranteed by the two anchor
SHAs plus the cell version. No separate hashes are tracked for derived files.

## Artifacts
| File | Location | Description |
|---|---|---|
| feature_separation_audit_master.csv | tier1_feature_separation_audit_outputs/ | locked audit master (241 features) |
| feature_separation_audit_dt_bins.csv | " | Δt-resolved separation profile (+ dt_median_min) |
| feature_separation_audit_drift.csv | " | between-date drift (slow timescale) |
| feature_separation_audit_summary.csv | " | origin × frame × class grouped summary |
| feature_separation_audit_class_rollup.csv | " | per-class rollup |
| operational_scale_registry_v1_0.csv | registries/ | per-feature engineering registry |
| operational_scale_registry_v1_0_meta.json | registries/ | registry metadata + provenance |
| Feature_Separation_Audit_Report_v1_1.docx | (repo root or /docs) | narrative + technical report |
| audit_fig1.png | (with report) | Figure 1 |
| tier1_feature_separation_audit.py (v2.1) | (scripts) | generating cell |

## Reproduction
1. Run `tier1_feature_separation_audit.py` v2.1 → master (must hash to `e5a6bad6…`) + dt_bins + drift.
2. Run the grouped-summary cell → summary + class_rollup.
3. Run the registry builder (SHA-guarded on the master) → registry v1.0 (must hash to `68319a2e…`) + meta.

## Method invariants
- Exploratory partition only (3,808 / 4,760 game-dates); outcome-blind.
- UTC timing via `Game_DateTime_UTC`; row-order join verified (0 mismatches / 57,635 events).
- near-concurrent = ≤45 min; `velocity_robust` = median sep ÷ median Δt in the 45–90 min bin.
- Per-frame scope: G-AZ for all bodies; G-LON/G-RA restricted to features touching {Asc, MC, VX, EA, MO}.

## Provisional / not yet established
- Operational classes are provisional (see above).
- `velocity_robust` is not meaningful for slow-contextual features (nulled in the registry).

## Next (NOT part of this lock)
- Gradient half: patched Step 2c on Tier A coverage-clean bodies — which same-slate discriminators sit on steep lift surfaces vs flat ones.
- Later: effective discriminability = spread × gradient × **stability** (persistence-weighted), to discount steep-but-unstable topology.
