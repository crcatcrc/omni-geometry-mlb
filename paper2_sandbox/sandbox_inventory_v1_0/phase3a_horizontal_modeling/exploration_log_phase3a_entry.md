## 2026-06-16 — Phase 3A · Horizontal 360° Model Prototyping (HS-vs-LS, exploratory)

Folder: `phase3a_horizontal_modeling/` · Full record: `PHASE3A_FINDINGS_LOG_v1_1.md` · Reproduction: `phase3a_analysis.py`
Status: closed and locked. Exploratory partition only; confirmatory holdout never opened.

### Question

First supervised pass on the completed horizontal aspect-feature system. Can the 192 horizontal 360° features distinguish high-scoring games (Total Runs ≥ 16) from low-scoring games (≤ 3) better than base-rate expectation? All work on the exploratory partition (46,152 events / 3,808 game-dates); modeling subset = the 8,486 HS∪LS games (HS 4,103, LS 4,383; base rate 0.516). Date-grouped 5-fold cross-validation throughout, seed 20260615. The holdout remained sealed at every step.

### How it unfolded

The session ran as a single descending staircase, each rung removing an explanation rather than adding a claim. We began with the leakage-free baseline the handoff prescribes — raw directed angles encoded as sin/cos, logistic regression — to establish an honest floor. We then asked whether the signal was nonlinear (tree models), whether it was diluted (support-gating, then L1 sparsity), and what survived selection (stability selection across 50 date-grouped resamples). That produced the one genuinely positive structural result of the phase. From there the work turned adversarial against our own signal: we introduced the ballpark as a control, which immediately dominated, and then spent the remainder testing whether anything of the geometry survived the obvious confounds — season, time-of-day, and an origin-class decomposition separating observer-dependent angle features from location-independent heliocentric ones. A park-tier stratification (the PI's own pre-registered intuition that geometry should be most visible where the park is least informative) surfaced a fast-helio lead inside neutral parks that looked, briefly, like the cleanest thing on the board; a degrees-of-freedom-matched permutation test then failed to confirm it. We closed by asking whether the park-to-park variation in separability was real (a stratified-permutation heterogeneity test, with the location-independent helio family as a built-in control) and whether it tracked any obvious park descriptor.

### What we found (headline level; tables in the findings log)

1. **Weak but real, and roughly linear.** Raw-angle logistic AUC 0.5768; L1-sparse best 0.5872 (C=0.1, ~114 of 384 columns retained). Tree models did not improve on the linear baseline (HistGradientBoosting 0.5611, RandomForest 0.5466 — the latter at ~7 min runtime for a worse result). A descriptor-support gate was inert (177 features → 0.5774). The signal is concentrated in a sparse subset, not diffuse, and not meaningfully nonlinear for this family.

2. **Stability selection reproduced the Phase 2B-1 descriptor structure — without seeing the support flags.** 64 features survive at selection-frequency ≥ 0.6. Per-class survival: helio 16/23 (≈70%), moon 17/39 (≈44%), angle 31/130 (≈24%). Predictive *weight*, however, is dominated by angle G-AZ slow-target features (the report's "selective high-lift" class), while the helio/moon backbone is consistently selected but small — the two-class structure of the descriptor survey, recovered independently inside a predictive model. Stable features overlap the support registry more than chance (0.94 vs 0.90). This is the sturdiest positive of the phase, and it is methodological, not predictive.

3. **The ballpark dominates.** Park identity alone (venue one-hot) reaches AUC 0.6415, well above geometry's 0.5872. Geometry adds only ≈ +0.015 over full park fixed-effects; park adds ≈ +0.069 over geometry. Roughly four-fifths of the apparent geometric signal was the ballpark — mechanistically unsurprising, since the highest-weight family (angle G-AZ) is computed at the park's own latitude/longitude and azimuth is the most location-sensitive coordinate.

4. **Season and time-of-day rejected; the residual is observer-dependent.** Calendar (day-of-year, two harmonics) alone is essentially chance (0.5132); geometry adds +0.0734 over calendar, and dropping all Earth-target features costs −0.0015 — season is not the carrier. Time-of-day adds nothing over park (−0.0023). Decomposing the residual-beyond-park by origin class: angle +0.0201, moon −0.0052, helio +0.0036 (null). The thin residual that survives park, season, and time lives entirely in the observer-dependent angle features; the clean-celestial heliocentric features add nothing over the ballpark.

5. **The fast-helio neutral-park lead is parked, not confirmed.** Stratifying by park tier, geometry was most detectable in neutral parks; within the neutral tier, after park and date/era controls, fast inner-planet (Mercury/Venus) heliocentric features added +0.0356 versus +0.0140 for the Earth-target (seasonal) helio. The physics distinction is sound — fast Me/Ve aspects cycle sub-seasonally and are not season or era. But a DOF-matched date-shift permutation put that +0.0356 inside the chance-feature null (null mean +0.0267, 95th percentile +0.0454, p ≈ 0.30). Status: **unconfirmed / parked** — a failure to confirm, not a disconfirmation. The lead is recorded, not claimed.

6. **Park heterogeneity is real.** Across the 27 parks with N ≥ 150, the spread of per-park separability exceeds sampling noise: geometry observed AUC-SD 0.0539 vs chance 0.0386 (p ≈ 0.002, ~49% of variance beyond chance); angle 0.0567 vs 0.0387 (p ≈ 0.001, ~53%). The genuine between-park angle-AUC SD is ≈ 0.04. Individual park rankings remain too noisy to trust (per-park SE ≈ 0.05); the earlier impression that neutral parks are uniquely strongest does not hold at the park level (tier means low 0.586 ≈ neutral 0.582 > high 0.559, all within noise).

7. **Heliocentric shows no heterogeneity — the control passes.** The location-independent helio family reads at chance spread (0.0391 vs 0.0394, p ≈ 0.47, 0% beyond chance), exactly as a family that cannot encode location should. This is the falsification check on F6: the heterogeneity lives where it physically can (observer-dependent angles) and is absent where it physically cannot.

8. **The heterogeneity is not explained by any obvious park descriptor.** Per-park angle separability shows no usable association with park HS-rate, extremeness (|HS-rate − 0.5|), night-game fraction, or median start hour (all |Spearman| ≤ 0.15, p > 0.4). Real structure, unexplained carrier — and the test is underpowered (n = 27), so "unexplained" is not "ruled out."

### Epistemic shape

This was a mostly-negative exploratory result, which is exactly what the sealed holdout is meant to protect. Horizontal geometry carries a weak HS-vs-LS signal, most of which is the ballpark; a small residual survives park, season, and time but lives entirely in observer-dependent features whose carrier we could not identify; the clean-celestial features are null; and a promising fast-helio lead did not survive a matched-DOF permutation. The one durable positive is structural rather than predictive — stability selection independently re-deriving the descriptor support structure — and it survives the confound debate entirely because it never used the outcome the way the AUC chase did.

### Process note

Three-way working method held: PI directs and decides, ChatGPT leads execution, Claude audits and backs up. Worth logging as process: several times the audit voice asserted a mechanism one step ahead of the evidence — "it's time-of-day," "helio is just the date," "the lead is dead," "no park structure" — and each was caught (by ChatGPT or by the PI's instinct) and corrected by running the test instead of asserting the conclusion. The PI's apples-and-oranges intuition about park inhomogeneity was vindicated by the heterogeneity finding (F6). The discipline that produced the clean result was refusing to let a tidy narrative outrun a permutation null.

### Artifacts (in `phase3a_horizontal_modeling/`)

- `PHASE3A_FINDINGS_LOG_v1_1.md` — full findings record (F1–F8 with tables).
- `phase3a_analysis.py` — single ordered reproduction script (state rebuild → F1–F8), seed 20260615, all data-contract oracles asserted.
- `STABLE_64_FEATURE_REPORT_v1.csv` — the 64 stably-selected features with weight, class, frame-pair, and support status.
- `PARK_GEOMETRY_REPORT_v1.csv` — per-park geometry/angle/helio AUC with noise band and tier.
- `PARK_DESCRIPTOR_TABLE_v1.csv` — per-park separability against start-time descriptors.

### Scope held

Holdout sealed and never read. No features deleted (retain-and-flag). Date-grouped CV throughout; splits by date, never by game. No vertical features. No confirmatory or production claims. All claims scoped to HS-vs-LS, horizontal families, exploratory partition.

### Parked / deferred (for a future session)

- **BHW-vs-GHL margin family** — never touched this phase; data-ready (`margin_expl` in the modeling state).
- **The decisive helio test** — whether fast Me/Ve aspects beat a *complexity-matched arbitrary fast-cycle date basis*; the only test that separates "the specific geometry matters" from "any flexible date model fits."
- **Park heterogeneity follow-up** — richer descriptors (altitude, roof, latitude, timezone, coastal) precision-weighted against angle-AUC; a feature×park interaction test gating a hierarchical / partial-pooling model (27 independent per-park fits are statistically unsound at ~250 games each).
- Vertical features remain out of scope for the horizontal phase.
