# CHANGELOG — OMNI Paper 2 / Track A Lineage

All notable methodological milestones. One entry per freeze.
Format: version — date — summary, decisions, baseline, next.

## [Track A Freeze v1.0] — 2026-06-24
Frozen Track A same-slate horizontal trigger population.

**Produced**
- 88 characterized features (48 geocentric + 40 heliocentric H-LON target); 0 dropped.
- Manifest: PHASE3D_TRACKA_FROZEN_MANIFEST_v1_0.csv
- Annex: 10 G-AZ × H-LON marginal frame-interaction features (preserved, not admitted).
- Track B routing: 4 limited-distribution helio targets (H-Jupiter, H-Saturn).

**Key decisions**
- Three-track architecture (A same-slate / B slow-context / C deferred targets).
- HS16 peaks treated as prior; peak structure recomputed fold-clean on HIGH≥14 / AVG 7–8.
- Heliocentric H-LON features audited on identical footing after a geocentric-only FSA gap was found and closed (Option 2).
- Same-slate reconstruction validated 48/48 on the known geo set before helio use.
- Multi-lobe adopted as the correct response-surface representation (single-peak rejected).
- Drop only if scatter_or_flat at BOTH 5° and 6°; per-feature frozen resolution (geo = FSA; helio = lower-circ-SD of {5,6}, tie→5°).

**Baseline at freeze**
- Honest leak-free reference: AUC ≈ 0.560 (date-grouped GroupKFold, nested encoding). No predictive improvement claimed by this phase.

**Known limitations carried forward**
- 88 is a floor: 311 geo features (bucket E) and the broader universe remain FSA-unaudited.
- Modality computed with label access (descriptive); must be recomputed fold-clean when engineered.
- Helio same-slate spread is angle-carried; helio target's independent contribution untested.
- No park/context control yet.

**Next**
- Fold-clean multi-lobe engineering over the frozen 88 → first leak-free test vs 0.560, as increment over park/context.
