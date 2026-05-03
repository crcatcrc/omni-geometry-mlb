# Paper Language (Working Capture)

Purpose: Collect paper-ready phrasing and interpretive statements during execution.
Scope: Language only (no results tables, no analysis steps, no code).
Status: Informal working document. Does not alter preregistration or execution logs.

---

## Core framing

- - Signal presence is invariant across coordinate transformations, while peak 
  localization is frame-dependent — even under nonlinear projection (G-AZ).

---

## Interpretation rules

- Three distinct mechanisms produce locks with peak count below the H1 support floor:
  (1) constrained apparent motion (SU/ME/VE),
  (2) sparse sample coverage (UR/NE/PL over a 25-year window),
  (3) combinations of the two.

- PFff and PFdn are calculated points whose formulas reference the Ascendant;
  Asc × PF features therefore measure the geometric separation between two
  non-identical but partially co-defined points.

---

## Notes

- This file refines language beyond exploratory (Phase C) and prereg (Document B) wording.
- All methodological claims must remain consistent with OSF preregistration.

- ---

## Projection artifacts (G-AZ specifically)

- In the azimuthal (G-AZ) target frame, outer bodies exhibit degenerate 
  high-target peaks (single-event maxima with capped lift), consistent with 
  non-uniform sampling under horizon projection. These effects do not survive 
  the pre-registered support floor and are treated as projection artifacts 
  rather than signal.

---

## Phase 2 forward-looking notes (not Phase 1 claims)

The bodies that fail the H1 support floor in Paper 1 (SU, ME, VE due to 
constrained apparent motion; UR, NE, PL due to sparse sample coverage over 
the 25-year window) are not abandoned — they are deferred to a Phase 2 
predictive-engine analysis where their geometric constraints can be modeled 
explicitly. Candidate Phase 2 approaches include coverage-aware features 
(effective angular support, occupancy histograms), hierarchical or pooled 
estimates to mitigate sparsity, regularized binning to stabilize low-count 
regions, and learned interaction terms rather than reliance on single-angle 
peaks. These are anticipated methodological extensions, not Paper 1 claims.

The G-AZ-origin construction (Asc G-AZ × body G-LON) produces the highest 
single-chunk H1 support rate observed in the Asc forward batch and a 
distribution of supported peak lifts extending into the 1.7–2.3 range at 
adequate support levels, exceeding the typical 1.35–1.55 range observed in 
same-coordinate constructions.

High-magnitude lift values are interpreted only within the constraint of the 
pre-registered support floor (smoothed_count ≥ 30); isolated high-lift peaks 
with low support are treated as sampling artifacts and excluded from 
interpretation.

Preliminary inspection suggests that feature strength varies systematically 
across constructions, with some features exhibiting both higher lift and 
greater support. Formal ranking of feature strength using coverage-weighted 
effect-size metrics is reserved for Phase 2 modeling.

Across all evaluated constructions, signal presence remains robust under 
coordinate transformation, while both peak localization and effect magnitude 
vary systematically with the choice of coordinate frame and transformation 
direction. This indicates that the observed structure is not an artifact of 
any single coordinate system, but rather reflects an underlying geometric 
relationship that is expressed differently under distinct observational 
projections.

---

## G-AZ direction asymmetry (Asc-6 vs Asc-7)

Cross-coordinate constructions involving azimuth exhibit directional asymmetry 
driven by sampling geometry: when G-AZ is the target frame, sparse projection 
leads to degenerate high-target peaks; when G-AZ is the origin frame, projection 
into G-LON restores sampling density and the same body pairs satisfy the support 
floor. This demonstrates that azimuth-dependent effects are governed by 
projection sampling rather than intrinsic absence of signal.

---

## Feature strength definition (descriptive)

Feature strength is not defined by peak lift alone. High-lift, low-support peaks 
are frequently produced by sparse sampling and are excluded by the pre-registered 
support floor. Robust features are instead characterized by consistent moderate 
lift (≈1.3-1.8), adequate support (counts ≥ 30), and persistence across 
coordinate systems and transformation directions.


