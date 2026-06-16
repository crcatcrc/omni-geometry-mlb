# PHASE 3A — Horizontal 360° Model Prototyping — FINDINGS LOG v1.1

OMNI Geometry MLB · Paper 2 Sandbox · HS-vs-LS · Horizontal systems · Exploratory partition only

**PI:** Courtney Roberts Conrad
**Date:** 16 June 2026
**Status:** Exploratory feature/model survey. Holdout sealed and never consulted. No confirmatory or production claims.
**Revision note (v1.1):** wording calibrated per review — F1 linearity claim removed, F4 "entirely"→"concentrated," F6 heterogeneity phrasing tightened, helio control split into standalone F7, headline and open-branch order updated.

---

## 0. Scope and discipline

- **Target:** distinguish high-scoring (HS, Total Runs ≥ 16) from low-scoring (LS, Total Runs ≤ 3) games.
- **Features:** the 192 completed horizontal 360° aspect features (angle, lunar, heliocentric-body origins), encoded leakage-free as raw directed angles → sin/cos (384 columns). No label-derived (lift/peak) encodings were used as model inputs.
- **Corpus / partition:** 57,635 games (2000–2024, 2002 excluded). Exploratory partition only: **46,152 events / 3,808 dates** (asserted on every build). HS∪LS modeling subset: **8,486 games (HS 4,103, LS 4,383; base rate 0.516)**.
- **Validation:** date-grouped 5-fold cross-validation throughout (GroupKFold on game-date). No game-level splits.
- **Non-negotiables held:** holdout sealed; no features deleted; exploratory only; no confirmatory language.

All AUC values below are out-of-fold ROC-AUC under date-grouped CV on the exploratory partition.

---

## 1. Findings

### F1 — Horizontal geometry carries a weak but real HS-vs-LS signal
Raw-angle sin/cos baseline: logistic **0.5768**, L1-sparse (C=0.1) **0.5872** (≈114/384 columns retained). Tree-based models did not improve on the logistic baseline under the encodings and hyperparameters tested (HistGradientBoosting 0.5611, RandomForest 0.5466); added model complexity provided no practical advantage in this exploratory survey. The signal is **sparse, not diffuse**.

### F2 — Stability selection independently reproduces the descriptor support structure
Across 50 date-grouped resamples (L1, C=0.1), 64 features were selected in ≥60% of resamples. Per-origin-class selection rates — helio ≈70% (16/23), moon ≈44% (17/39), angle ≈24% (31/130) — and the predictive-weight concentration in angle G-AZ slow-target features reproduce the two-class structure of the Phase 2B-1 registry **without the model ever seeing the support flags**. This is the sturdiest positive of the phase: methodological corroboration of the descriptor work, not a predictive claim.

### F3 — Ballpark dominates prediction
Complete park fixed-effects (venue one-hot, 80 parks): **park-only 0.6415**, the single strongest predictor produced. Geometry-only 0.5872. Geometry + park 0.6565.
- Δ sky-beyond-park = **+0.0150**
- Δ park-beyond-sky = **+0.0693**

Most of geometry's apparent separability overlaps park identity. A small geometry residual beyond full park fixed-effects survives.

### F4 — The residual-beyond-park is observer-dependent; carrier unidentified
The ~+0.015 residual was tested against the leading mundane confounds:
- **Season** (calendar-only 0.5132; geometry+calendar adds +0.0734 over calendar): rejected as the explanation. Dropping all Earth-target (solar-longitude) features costs only −0.0015.
- **Time-of-day** (park+time vs park = −0.0023; angle-over-park+time = +0.0135): rejected; the residual survives start-hour control.
- **Origin class over park:** angle **+0.0201**, moon −0.0052, helio **+0.0036** (≈ null). The surviving residual is **concentrated in the observer-dependent angle features**; the location-independent heliocentric features add nothing beyond park.

Defensible statement: *for HS-vs-LS, heliocentric body–body features add no meaningful predictive information beyond park; the residual-beyond-park is concentrated in observer-dependent angle features.* What that residual **is** (finer-than-venue geography, local clock, daylight, scheduling, or something else) is not identified.

### F5 — Fast Mercury/Venus neutral-park lead: failed confirmation (parked)
Within the neutral park tercile, controlling park + date/era, fast inner-planet heliocentric aspects (Me/Ve × non-Earth, 21 features) added **+0.0356** over park+date, versus +0.0140 for the 2 Earth-target (seasonal) helio features. This was the most attractive lead of the session.

It did **not** survive a degrees-of-freedom-matched date-shift permutation (same 21 features, sky decorrelated from games): null mean **+0.0267**, null 95th percentile **+0.0454**, true Δ **+0.0356**, **p = 0.298**. The observed effect is indistinguishable from what 21 autocorrelated fast features produce by chance.

**Status: unconfirmed / parked — failure to confirm, not disconfirmation.** The physics point stands (fast Me/Ve cycles are sub-seasonal and not calendar-locked, so they are genuinely *not* season or era); the empirical signal simply does not separate from chance feature-fitting at this sample size.

### F6 — Park-to-park heterogeneity in separability is real, and specific to angle features
Omnibus stratified-permutation heterogeneity test (27 parks, N≥150; per-park within-park AUC of the global model; null = random class-balanced assignment of games to park-sized bins):

| System | obs AUC-SD | chance SD | 95% null SD | beyond-chance | p |
|---|---|---|---|---|---|
| geometry (all) | 0.0539 | 0.0386 | [0.0283, 0.0496] | ~49% | **0.002** |
| angle | 0.0567 | 0.0387 | [0.0279, 0.0494] | ~53% | **0.001** |
| helio | 0.0391 | 0.0394 | [0.0286, 0.0505] | 0% | 0.474 |

The predictive separability associated with horizontal geometry varies across parks beyond what would be expected from sampling variation alone, and the variation is **concentrated in the observer-dependent angle family**. Genuine between-park SD of angle-AUC ≈ 0.04 (noise floor removed).

**Important limit:** the omnibus establishes that the *collection* of parks differs; individual park ranks remain noisy (per-park AUC SE ~0.05). No single park-vs-park ordering is trustworthy.

### F7 — Heliocentric separability shows no park-to-park heterogeneity (internal control)
Unlike the angle and combined-geometry systems, the location-independent heliocentric system showed **no evidence** of park-to-park heterogeneity (obs SD 0.0391 vs null 0.0394, **p = 0.474**, 0% beyond chance). This serves as an internal calibration check on the heterogeneity framework: a feature family that *cannot* carry park-specific information correctly shows none. It indicates the observed park structure is a property of the observer-dependent features specifically, not a generic artifact of the test applied to any feature family. This is arguably the cleanest single result of the park investigation.

### F8 — The heterogeneity is not accounted for by obvious park descriptors
Correlations of angle_AUC / geo_AUC against per-park HS_rate, |HS_rate−0.5| (extremeness), night-game fraction, and median start hour (n=27): all |Spearman| ≤ 0.15, all p > 0.4. The largest single coefficient (geo_AUC vs HS_rate, Pearson −0.23, p=0.24) is directionally consistent with extreme parks being slightly harder to separate, but is not significant.

At the available power (n=27, AUC SE ~0.05), **run environment, park extremeness, day/night mix, and start time do not account for the heterogeneity.** This is an underpowered null — these descriptors are not *ruled out*, but they do not explain the structure, which justifies moving to richer park descriptors rather than declaring the question closed.

---

## 2. What is NOT established

- The **carrier** of the angle residual / park heterogeneity (geography, local clock, daylight, travel/scheduling, or genuine geometry) — unidentified.
- Whether the per-park geometry→outcome **mapping** differs by park, versus the same signal being merely more *detectable* in some parks. Not tested. (The powered way to ask is a feature×park interaction on the stable feature set; per-park independent models are ruled out by power — ~250 games vs 260 angle columns.)
- Any **out-of-sample / holdout** behavior. The confirmatory partition was never consulted.
- The **BHW-vs-GHL** margin family — untested (margin labels are stashed for the next session).
- Vertical features — out of scope for Phase 3.

---

## 3. Headline conclusion

For HS-vs-LS on the horizontal feature system, exploratory partition: the ballpark is the dominant predictor (0.642); horizontal geometry adds only a small residual beyond it (~+0.015), which is observer-dependent and of unidentified carrier; and there is **statistically real park-to-park variation in angle-feature separability that the obvious park descriptors do not explain.** The location-independent heliocentric control showed **no corresponding heterogeneity** — the cleanest single result of the park investigation, and evidence that the structure is specific to observer-dependent features rather than a generic property of all feature families.

Taken together, this is a stronger and cleaner conclusion than any of the single-feature or neutral-park narratives examined and discarded along the way — it is a result about the parks and the observer-dependent feature family, with a clean internal control, rather than a single AUC number.

---

## 4. Open branches for the next session (no commitment)

1. **BHW-vs-GHL margin family** — the untouched second outcome target, already funded by existing data (margin labels stashed). The most natural next independent question.
2. **Richer park descriptors** to attack F6/F8: latitude, roof/open-air, timezone, coastal/interior, altitude, travel patterns. Relate to angle-AUC with precision weighting (per-park SE), AUC held as the noisy outcome; stability-validate any clustering.
3. **Do per-park mappings differ?** Feature×park interaction test on the stable angle feature set (powered; few features). If real → a hierarchical / partial-pooling model (park-specific coefficients shrunk to a global mean) is the correct tool — not independent per-park fits.

---

## 5. Provenance and artifacts

- Engine / registry: descriptor engine schema 2.0.2; horizontal feature registry v1.0 (768 rows, 192 features, 683 supported / 85 flagged). Authoritative support column: `support_flag` (peak_lift>1.15 ∧ peak_count≥30 ∧ lock_succeeded). `h1_supported` is stale and was not used.
- Source matrices (raw directed angles, 57,635 rows, row-aligned): Cross-System G-AZ/G-LON/G-RA → H-LON, and H-LON → H-LON.
- Saved tables: `STABLE_64_FEATURE_REPORT_v1.csv`, `PARK_GEOMETRY_REPORT_v1.csv`, `PARK_DESCRIPTOR_TABLE_v1.csv`.
- Seed 20260615. Environment: Python 3.12, scikit-learn 1.6.1.
