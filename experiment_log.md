# OMNI Project — Experiment Log

## Purpose
This log records all **project-level decisions**.
It is not a run log. Engine runs are recorded automatically in `run_manifest.csv`.

A decision not recorded here does not exist.

---

## Entry Format (MANDATORY)

Each entry must follow this exact structure:

### [YYYY-MM-DD] — <Short Title>

**Type:** <Decision | Approval | Change | Deviation | Lock | Issue>

**Context:**
Brief description of what triggered this entry.

**Decision:**
Exact decision made. Must be explicit and unambiguous.

**Rationale:**
Why this decision was made.

**Implications:**
What this affects (analysis, data, code, writeups, etc.)

**Related Artifacts:**
- Documents:
- Files:
- Runs (if applicable):

**Status:**
<Pending | Active | Superseded | Locked>

---

## Entry Types

### Decision
A choice between alternatives.

### Approval
Formal acceptance (e.g., locking a document, approving figures).

### Change
Modification to plan or configuration.

### Deviation
Any departure from pre-registration (must be justified).

### Lock
Declaring something immutable (e.g., Phase C results).

### Issue
Problem identified requiring tracking.

---

## Rules

- All major decisions MUST be logged.
- No retroactive entries (see Backfill exception below).
- No editing past entries (append new entry instead).
- Keep entries concise but complete.
- Use exact dates (no relative references).

---

## Initial Backfill (one-time exception)

The first commit of this log includes a backfill of major project decisions made before the log existed.

Backfill entries:
- are dated to the actual decision date
- are clearly marked at the top as:
  **"BACKFILL — recorded retroactively from project history"**

After the first non-backfill entry:
→ the no-retroactive rule applies strictly

---

## Relationship to run_manifest.csv

- `run_manifest.csv` → automatic engine run log
- `experiment_log.md` → human decision log

Rules:
- If a decision is not logged → it does not exist
- If a run is not in the manifest → it does not exist

---

## Example Entry

### [2026-04-29] — Lock Phase C Results

**Type:** Lock

**Context:**
Phase C symmetry analysis completed and reviewed.

**Decision:**
Phase C results, figures, and writeup v2.3 are locked.

**Rationale:**
All diagnostics passed; no further iteration required.

**Implications:**
- No re-runs of Phase C
- Figures treated as canonical
- Subsequent work moves to batch expansion

**Related Artifacts:**
- Documents: Phase C writeup v2.3
- Files: phase_c_*.csv
- Runs: Phase C final execution set

**Status:**
Locked
### [2026-XX-XX] — OSF Pre-registration Submitted

**Type:** Lock

**Context:**
Completion of preregistration prior to confirmatory batch execution.

**Decision:**
OSF registration submitted and locked.

**Rationale:**
Required to enforce confirmatory analysis integrity.

**Implications:**
- Forward batch may begin
- No adaptive changes allowed
- Deviations require formal amendment

**Related Artifacts:**
- OSF: https://osf.io/yhxt4/overview

**Status:**
Locked
### [2026-05-01] — Adopt Hybrid Batch Execution Protocol

**Type:** Decision

**Context:**
Post-OSF execution planning for confirmatory forward batch.

**Decision:**
Forward batch will begin in safe mode for Asc-1, Asc-2, and Asc-3. Each of these chunks will be run and inspected individually before proceeding. After successful completion of the first three same-coordinate Asc chunks, execution may proceed in efficient controlled mode, with continued adherence to locked feature lists, snapshot requirements, dedupe behavior, and no adaptive changes.

**Rationale:**
The first three Asc chunks are same-coordinate and most directly comparable to already-locked Asc × MO exploratory results. Running these individually provides an early integrity check before accelerating batch execution.

**Implications:**
- Asc-1, Asc-2, and Asc-3 are treated as guarded launch chunks.
- No scope, threshold, feature, or engine changes are permitted.
- Later chunks may be executed more efficiently once early behavior is verified.

**Related Artifacts:**
- OSF: https://osf.io/yhxt4/overview
- Documents: Document C v1.1; Document B v4
- Files: cell_v2_batch_v2_0_2_stepB_revF.py
- ### [2026-05-01] — Note Interpretive Caveats for PF and Inner-Planet Features

**Type:** Issue

**Context:**
Before launching Asc-1, two structural considerations were identified: PFff/PFdn are calculated points whose formulas reference the Ascendant, and SU/ME/VE geocentric G-LON/G-RA features may exhibit constrained apparent motion.

**Decision:**
No scope change will be made. PFff, PFdn, SU, ME, and VE remain in the pre-registered feature space and will be executed as specified.

**Rationale:**
The OSF pre-registration and PROJECT_SCOPE define the full feature space. Removing or altering these features after registration would constitute an adaptive scope change. Asc × PF features measure the geometric separation between two non-identical but partially co-defined points, while constrained-motion features are handled by the engine’s existing support rules.

**Implications:**
These features will be retained in execution but interpreted cautiously in later reporting. Any mathematical dependence, partial co-definition, constrained-motion behavior, insufficient-support outcome, or “no lock” result will be reported as diagnostic information rather than used as a basis for exclusion.

**Related Artifacts:**
- OSF: https://osf.io/yhxt4/overview
- Documents: PROJECT_SCOPE.md; OMNI Naming Conventions Reference v2
- Files: cell_v2_batch_v2_0_2_stepB_revF.py

**Status:**
Active

**Status:**
Active

### [2026-05-02] — Apply H1 Support-Floor Interpretation Rule

**Type:** Decision

**Context:**
Asc-1 produced several rows with `lock_succeeded = True` but `peak_smoothed_count < 30`, especially among SU, ME, VE, NE, and PL features.

**Decision:**
For confirmatory H1 evaluation, a target-evaluation counts as supported only if all three conditions are met:

1. `lock_succeeded = True`
2. `peak_smoothed_lift > 1.15`
3. `peak_smoothed_count >= 30`

Rows failing the support floor are retained in the registry but classified as unsupported for H1.

**Rationale:**
The OSF pre-registration requires peak smoothed lift above threshold with sufficient support. The engine’s `lock_succeeded` flag records successful lock computation, but H1 support requires the additional count floor.

Low-count cases may arise from constrained apparent motion, sparse sample coverage over the 25-year window, or other distributional limits. These are diagnostic outcomes, not grounds for changing scope.

**Implications:**
- Asc-1 remains valid.
- Low-count rows remain reported.
- Unsupported rows contribute to the H1 denominator but not the numerator.
- This rule applies uniformly to all 54 chunks.
- No engine modification is made.

**Related Artifacts:**
- OSF: https://osf.io/yhxt4/overview
- Documents: PROJECT_SCOPE.docx; Document B v4; Document C v1.1
- Files: omni_feature_registry.csv; cell_v2_batch_v2_0_2_stepB_revF.py

**Status:**
Active
### [2026-05-02] — Missing PF G-AZ Features in Asc-3

**Type:** Issue

**Context:**
Asc-3 (G-AZ same-coordinate) execution skipped two requested features:
- Asc x PFff G-AZ
- Asc x PFdn G-AZ

The engine reported both columns as missing from the G-AZ aspect feature file.

**Decision:**
These features are recorded as unavailable in the current G-AZ aspect dataset. No rerun, reconstruction, substitution, or scope change will be performed.

**Rationale:**
The missing columns reflect the contents of the locked aspect feature file used for execution. This is treated strictly as a data-availability constraint. Post-registration feature reconstruction or reinterpretation is not permitted during confirmatory execution. The absence of these columns is not interpreted as a theoretical impossibility, and no scope reduction is applied.

**Implications:**
- Asc-3 produced 15 successful features / 30 target-evaluations.
- PFff/PFdn G-AZ evaluations are unavailable for Asc-3 reporting.
- These evaluations are excluded from H1 numerator calculations.
- Final denominator treatment will be applied uniformly across all chunks after full execution is complete.
- Wherever PF G-AZ or other unavailable columns occur in subsequent chunks, the same treatment applies: skip silently, log the omission, and do not rerun.
- No engine code, feature definitions, or data-generation steps are modified.

**Related Artifacts:**
- OSF: https://osf.io/yhxt4/overview
- Run: Asc-3 G-AZ same-coordinate batch
- File: MLB 2000-no02-2024 G-AZ to G-AZ aspect features.csv
- Output: omni_feature_registry.csv

**Status:**
Active

### [2026-05-03] — Asc-6 Dedupe Spike and G-AZ Degenerate Peaks

**Type:** Observation

**Context:**
Asc-6 (G-LON → G-AZ) produced an elevated pre-dedupe row count (174 → 240) with post-dedupe resolution to 206 (net +32).

**Observation:**
- The inflated pre-dedupe count indicates duplicate inserts within the run; post-run dedupe collapsed to the expected canonical set.
- G-AZ High-target peaks for UR/NE/PL showed identical capped lift values (~11.25) with count ≈ 1.

**Decision:**
- Treat the dedupe spike as a benign within-run duplication artifact; no rerun.
- Classify G-AZ High-target outer-planet peaks as degenerate (single-event) and exclude via the H1 support floor.

**Rationale:**
Post-dedupe registry state is authoritative. Identical capped lifts with count ≈ 1 across multiple bodies indicate projection/smoothing artifacts, not stable signal.

**Implications:**
- H1 counts unaffected (supported 25/34).
- No changes to engine or feature definitions during confirmatory phase.

---


### [2026-05-04] — Forward-Batch Domain Restrictions and Measurement-System Characterization (Pre-MC Batch)

**Type:** Issue (preemptive, prior to MC batch execution)

**Context:**
The pre-registered scope (OSF: https://osf.io/yhxt4/overview; Document B v4 Section 7.8) defines 1,710 target-evaluations across:
  (4 angles × 17 bodies) + (MO × 14 bodies) + (ME × 13 bodies)
  = 95 origin-target pairs × 9 constructions × 2 outcomes
  = 1,710 target-evaluations.

Three structural properties of the data have been identified that affect the testable confirmatory scope. All three are identified prior to MC batch execution and consolidated into this single preemptive Issue entry. None of these properties was created during Phase 1; each reflects either a geometric definition of an angle origin, a Swiss Ephemeris pipeline scope decision predating Phase 1, or an empirical sampling characteristic of the locked dataset.

This entry replaces and extends the 2026-05-02 PoF G-AZ entry (which is preserved for archival traceability but superseded by this consolidated treatment).

---

**Mechanism 1 — MC and VX G-AZ structural exclusion**

*Geometric basis.* Midheaven (MC) is the point where the local meridian intersects the ecliptic at upper culmination; its azimuth is fixed at approximately 180° (north-hemisphere convention) or 0° (south-hemisphere convention). Vertex (VX) is the point where the prime vertical intersects the ecliptic in the western half of the sky; its azimuth is fixed near 270°. Across the 25-year sample, MC's and VX's azimuthal coordinates occupy narrow, non-uniform domains reflecting only local-latitude variation rather than wheel-traversing variation. Their azimuthal positions were not generated by the Swiss Ephemeris pipeline (predating Phase 1) on the basis that their structurally constrained azimuth distributions would not support meaningful 360° angular-separation feature construction.

*Decision.* Coordinate constructions in which MC's or VX's azimuth would serve as the primary axis are excluded from confirmatory analysis on the grounds that their azimuthal distributions occupy a narrow, non-uniform domain that does not approximate a circular sampling space, thereby violating the assumptions required for 0–360° angular-separation feature construction.

Per origin (MC, VX), three of nine pre-registered constructions are excluded: same-coordinate G-AZ (chunk position 3); G-AZ-origin × G-LON cross-coordinate (position 7); G-AZ-origin × G-RA cross-coordinate (position 9). The remaining six constructions per origin (positions 1, 2, 4, 5, 6, 8) are unaffected.

*Excluded evaluations from Mechanism 1:* 2 origins × 3 constructions × 17 bodies × 2 outcomes = **204 evaluations**.

---

**Mechanism 2 — PoF aspect-file coverage**

*Empirical basis.* A column-availability diagnostic across all nine aspect feature files confirms that PFff and PFdn (Part of Fortune formulary and dynamic variants) are absent as feature-pair components in three of the nine aspect files: same-coordinate G-AZ-to-G-AZ; cross-coordinate G-AZ-to-G-LON; cross-coordinate G-AZ-to-G-RA. The absence is uniform across all four angle origins (Asc, MC, VX, EA) and reflects a Swiss Ephemeris pipeline scope decision predating Phase 1: PoF G-AZ values were generated as base positions (present in the base positions file) but were not propagated as origin-side components into G-AZ-origin aspect feature files. This condition was first observed during Asc-3 execution and logged on 2026-05-02; the present entry provides the consolidated denominator math.

*Decision.* PoF feature-pair evaluations in the three affected aspect files are recorded as attempted-but-unavailable in the registry and excluded from H1 numerator calculations. No rerun, reconstruction, substitution, or pipeline regeneration is performed during confirmatory analysis.

*Excluded evaluations from Mechanism 2 (after de-duplication with Mechanism 1, since MC and VX G-AZ-origin cases are already excluded structurally):* Asc and EA contribute 2 origins × 3 aspect files × 2 PoF variants × 2 outcomes = **24 net additional evaluations**.

---

**Mechanism 3 — Angle-origin G-AZ coverage characterization (descriptive, not exclusionary)**

*Empirical basis.* A coverage diagnostic was performed for all four angle origins across all three coordinate frames. Asc and EA G-AZ coordinates occupy bounded azimuthal arcs (Asc: 53°–126°, 72/360 occupied bins, ~20% wheel occupancy; EA: 68°–112°, 45/360 occupied bins, ~12.5% wheel occupancy). Within these bounded arcs, sampling is dense (largest gap between consecutive occupied bins: 3° for Asc, 1° for EA). G-LON and G-RA coordinates for all four angles span the full 0–360° domain with ≥97% occupancy. MC and VX G-AZ are not in the pipeline (Mechanism 1).

*Interpretive consequence.* The bounded angle-origin G-AZ coverage does **not** invalidate angular-separation feature construction. Angular-separation features are computed as circular differences modulo 360°: the domain of angular separation is not constrained by the domain of the origin coordinate. When a bounded-origin coordinate (Asc G-AZ or EA G-AZ) is paired with a target whose azimuthal coverage spans the full circular domain through aggregate sampling under daily rotation, the resulting separation values occupy the full 0–360° range. The bounded origin functions as a moving reference frame rather than a limiting domain.

The bounded-arc characterization does, however, distinguish a **local (concentration) signal regime** from the **global signal regime** of full-circle G-LON / G-RA constructions. In the local regime, observations are concentrated within a bounded eastern azimuthal sector, amplifying contrast in angular-separation distributions and producing localized high-amplitude lift values. Cross-regime lift comparisons are descriptive only; coverage-aware effect-size estimation across regimes is reserved for Phase 2 modeling.

*No evaluations are excluded by Mechanism 3.* This mechanism is descriptive characterization that informs the interpretive framework (Methods v4 Section 2.2 four-regime framework) without modifying confirmatory testing scope.

---

**Combined adjusted scope:**

| Item | Evaluations |
|---|---|
| Pre-registered scope | 1,710 |
| Excluded by Mechanism 1 (MC/VX G-AZ structural) | −204 |
| Net additional excluded by Mechanism 2 (PoF aspect-file, after de-duplication) | −24 |
| Mechanism 3 (descriptive only) | 0 |
| **Adjusted confirmatory testable scope** | **1,482** |

**Per-origin attempted evaluations:**

| Origin | Pre-registered | Adjusted | Status |
|---|---|---|---|
| Asc | 306 | 294 | complete (215 supported, 73.1%); see Asc Batch Summary v4 |
| MC | 306 | 204 | 6 chunks (positions 1, 2, 4, 5, 6, 8); PoF available in all 6 valid aspect files |
| VX | 306 | 204 | 6 chunks (same structure as MC); PoF available in all 6 valid aspect files |
| EA | 306 | 294 | 9 chunks; PoF unavailable in same 3 aspect files as Asc |
| MO origin | 252 | 252 | full scope retained |
| ME origin | 234 | 234 | full scope retained |
| **Total** | **1,710** | **1,482** | |

---

**Rationale:**

All three mechanisms reflect structural properties of the data — geometric (Mechanism 1), pipeline-scope (Mechanism 2), and empirical sampling characteristic (Mechanism 3) — that are characterized rather than discovered during Phase 1. None constitutes scope reduction or post hoc filtering. Mechanism 1 and Mechanism 2 represent domain restrictions: the excluded configurations cannot produce valid test statistics under the pre-registered analytical framework; they are not "tested and excluded" but "not testable under the present measurement system." Mechanism 3 is descriptive characterization that does not modify scope.

All three mechanisms were identified outside the H1 testing process: Mechanism 1 prior to MC batch execution; Mechanism 2 prior to Asc-3 execution (logged 2026-05-02); Mechanism 3 prior to MC batch execution (during the present consolidated review). The OSF pre-registration's deviation policy applies: this is an **Issue** (preemptive methodological clarification and characterization), not a Deviation (post-execution change to confirmatory rules).

All three mechanisms were identified independently of outcome-variable behavior and prior to forward-batch execution beyond Asc, ensuring that no exclusion decision was informed by feature performance.

The H1 support criterion (peak_smoothed_lift > 1.15, peak_smoothed_count ≥ 30, lock_succeeded = True) is unchanged. The 50% pre-registered H1 panel-wide threshold is unchanged. No features are removed from the registry.

---

**Implications:**

- Panel-wide H1 support across all six origins will be reported against the **1,482-evaluation denominator** with explicit statement of the 228-evaluation domain restriction (204 + 24).
- Asc batch H1 numerator (215 supported) and denominator (294 attempted) are unaffected.
- Forward-batch chunks proceed as configured; MC and VX execute 6 chunks each rather than 9.
- The four-regime sampling-geometry framework (Methods v4 Section 2.2) and the local/global signal regime distinction (Methods v4 Section 2.2 and §2.4) become the interpretive infrastructure for forward batches and for cross-origin comparison.
- Coverage-aware modeling for the three identified mechanisms is reserved for Phase 2 (separate pre-registration document).

---

**Phase 2 considerations:**

PoF G-AZ position values exist in the base positions file and may be revisited in Phase 2 modeling under coverage-aware feature engineering. MC G-AZ and VX G-AZ as quasi-fixed directional anchors may also be revisited in Phase 2 as narrow-band features for fine-grained intra-day temporal differentiation. Concentration-regime lift inflation may be addressed in Phase 2 via density normalization, occupied-domain scaling, or hierarchical pooling. None of these revisitations affects Phase 1 confirmatory conclusions.

---

**Related artifacts:**

- OSF: https://osf.io/yhxt4/overview
- Document B v4 Section 7.8 (scope derivation: 1,710 evaluations)
- experiment_log.md entry of 2026-05-02 (Mechanism 2 first observation; superseded by this consolidated entry)
- Asc Batch Summary v4 (Asc batch completed under existing handling; revision to v5 underway to reference this consolidated entry)
- paper_language.md (sampling-geometry principle; two-regime architecture; high-lift caveat — additions pending)
- Methods v4 Section 2.2 (four-regime framework integrating Mechanisms 1 and 3)
- Methods v4 Section 2.2.1 (angle-origin coverage diagnostic; Mechanism 3 empirical table)
- Methods v4 Section 2.10 (pre-registration compliance; adjusted denominator math)

---

**Status:** Active

MC batch complete and locked, panel-wide 158/204 = 77.5%, six chunks executed, summary cross-reviewed and locked.

2026-05-09 — VX batch complete and locked. Six chunks executed under engine v2.0.2: VX-1 (G-LON same), VX-2 (G-RA same), VX-4 (G-LON × G-RA), VX-5 (G-RA × G-LON), VX-6 (G-LON × G-AZ), VX-8 (G-RA × G-AZ). Chunks 3/7/9 excluded by Filter M1 (VX G-AZ origin). Panel-wide H1 support 163/204 = 79.9% — highest among completed Phase 1 origin batches. Coverage-clean detection robustness 132/132 with Tier A 7-block 72/72 = 100% anchor (strongest temporal-validation outcome in Phase 1 to date). Two new structural findings: (1) coverage-interaction efficiency on sparse outer planets in the global regime — 24/24 outer-planet support across global-regime VX chunks; (2) distinct stability topology vs MC — VX produces binary stabilize-or-collapse on sparse outers (27 anchor / 0 persistent / 9 fragile), MC produces graduated persistence (12 / 16 / 8). VX Batch Summary v1.1-final cross-reviewed with ChatG and locked. Cleared to begin EA batch.

2026-05-08 — EA batch complete and locked. Nine chunks executed under engine v2.0.2: EA-1 (G-LON same), EA-2 (G-RA same), EA-3 (G-AZ same, concentration), EA-4 (G-LON × G-RA), EA-5 (G-RA × G-LON), EA-6 (G-LON × G-AZ), EA-7 (G-AZ × G-LON, concentration), EA-8 (G-RA × G-AZ), EA-9 (G-AZ × G-RA, concentration). Panel-wide H1 support 232/294 = 78.9%. Coverage-clean detection robustness 222/222. Phase B 7-block anchor+persistent 245/294 = 83.3%. Within-origin regime split: global 180/204 = 88.2%, concentration 65/90 = 72.2% — first within-origin demonstration that concentration trades higher Phase A support for lower temporal stability. New cross-origin structural law (Statement EA-8): target-G-AZ sparse-outer suppression converges across all four origins (Asc/MC/VX/EA), establishing it as a property of the measurement system rather than origin-specific. EA Batch Summary v1.1-final cross-reviewed with ChatG (parallel summary produced; key contributions incorporated) and locked. Cleared to begin MO batch.
