# Phase 3D — Track A Freeze (v1.0)

## Overview

This directory contains the complete research record for the Phase 3D construction and freeze of the **Track A same-slate horizontal trigger population** used in the OMNI MLB predictive engine.

The objective of this phase was **not** to build a predictive model. Instead, the objective was to identify, characterize, validate, and freeze the population of horizontal aspect features that are operationally suitable for later feature engineering.

The resulting frozen Track A population consists of:

* **48 geocentric features**
* **40 heliocentric H-LON target features**
* **88 total characterized features**
* **0 features removed under the adopted dual-resolution scatter rule**

The work documented here established that heliocentric angle-target features belong on essentially equal footing with the geocentric population after matched-resolution characterization.
Honest leak-free baseline at phase entry: AUC ≈ 0.560 (date-grouped, nested encoding). Track A was constructed to be engineered against this baseline; no predictive improvement is claimed by this phase."

---

## Directory Contents

### manifests/

Final frozen feature populations.

Primary artifact:

* `PHASE3D_TRACKA_FROZEN_MANIFEST_v1_0.csv`

---

### characterization/

Feature characterization tables.

Includes:

* Combined geo + helio characterization
* Matched-resolution heliocentric characterization

---

### diagnostics/

Supporting analyses leading to the frozen population.

Includes:

* Single-peak recomputation
* Modality diagnostics
* Heliocentric same-slate audit
* Track B routing

---

### reports/

Narrative documentation describing the complete methodology, rationale, decisions, and interpretation of this phase.

---

## Major Decisions Frozen in v1.0

* Coverage-clean population used as the starting universe.
* Three-track architecture adopted:

  * Track A — same-slate trigger features.
  * Track B — slow-context / limited-distribution features.
  * Track C — deferred alternate targets.
* Heliocentric H-LON target features audited on the same operational footing as geocentric features.
* Multi-lobe response surfaces adopted as the correct representation of horizontal geometry.
* Feature removal permitted only if scatter-or-flat at both 5° and 6°.
* Per-feature frozen resolution adopted:

  * Geocentric: FSA recommended resolution.
  * Heliocentric: lower circular-SD of 5° or 6°.

---

## Current Status

Phase 3D Track A is complete.

The frozen manifest produced here becomes the sole input population for the next phase:

**Fold-clean multi-lobe feature engineering.**

No additional raw feature selection should occur before completion of the engineering layer.

---

## Repository Version

Phase 3D Track A Freeze

Version 1.0

June 2026
