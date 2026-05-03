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
