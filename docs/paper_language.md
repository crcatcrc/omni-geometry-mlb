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


---

## Sampling-Geometry Principle (Locked)

Angular-separation features are defined over a circular domain (0–360°) computed as modular differences between two coordinates. The domain of angular separation is therefore not constrained by the domain of either contributing coordinate individually.

When one coordinate occupies a bounded domain (e.g., angle-origin G-AZ restricted to a local azimuthal arc) and the paired coordinate spans the full circular domain through aggregate sampling (e.g., target-body G-AZ under Earth's daily rotation), the resulting separation values populate the full 0–360° domain. The bounded coordinate functions as a moving reference frame rather than a limiting domain.

This principle justifies the use of bounded-origin coordinate systems (e.g., Asc G-AZ, EA G-AZ) in angular feature construction and distinguishes coordinate-domain coverage from separation-domain coverage.

---

## Two-Regime Signal Architecture (Locked)

Angular feature constructions in this study partition into two structurally distinct signal regimes based on coordinate sampling geometry:

**Global Regime**

Constructions in which both origin and target coordinates span the full 0–360° domain (e.g., G-LON, G-RA, and G-AZ as target under aggregate sampling). Observations are distributed across the full circular domain, and effect sizes reflect global structure in angular-separation space.

**Local (Concentration) Regime**

Constructions in which one coordinate (typically the origin) occupies a bounded domain (e.g., Asc G-AZ or EA G-AZ), while the paired coordinate spans the full domain. Observations are concentrated within a restricted sector defined by the bounded coordinate, producing localized contrast in angular-separation distributions.

These regimes are properties of the measurement system rather than of the underlying celestial relationships. Comparisons of effect size across regimes must account for differences in sampling geometry.

---

## Concentration-Regime Caveat (Locked)

Elevated lift values observed in concentration-regime constructions (e.g., G-AZ-origin pairings) arise from the concentration of observations within a bounded sampling domain, which increases contrast in angular-separation distributions relative to a global baseline.

This amplification reflects measurement geometry rather than necessarily stronger underlying relationships. However, the presence of statistically supported signal (i.e., satisfying pre-registered support criteria) remains valid.

Accordingly:
- High lift combined with low sample support is treated as unstable (degenerate or sparse).
- High lift combined with adequate support is interpreted as a valid signal expressed under concentration.
- Cross-regime comparisons of lift magnitude (concentration vs global constructions) are descriptive only.

Comparable effect-size estimation across regimes is reserved for Phase 2 modeling using coverage-aware methods.



