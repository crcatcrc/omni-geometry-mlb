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
