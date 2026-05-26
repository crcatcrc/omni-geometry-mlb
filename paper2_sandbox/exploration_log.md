# OMNI Paper 2 Sandbox — Exploration Log

Append-only project log for the OMNI Paper 2 exploratory phase. Each entry records what was considered, what was attempted, and the disposition. The log is the audit substrate for the researcher-degrees-of-freedom disclosure required under Charter §3.1 and the working substrate for ChatG hostile review at the conversion threshold (Charter §8). The log is frozen and hashed at sandbox closure per Charter §11.

## Entry format

- **Timestamp** (ISO 8601 UTC, e.g. `2026-05-25T17:30:00Z`)
- **Type** ∈ {`hypothesis`, `feature`, `model`, `outcome-class`, `stratum`, `partition-diagnostic`, `lock-event`, `sequencing`}
- **Entity** — the thing under consideration
- **Motivation** — why this is being considered
- **Outcome** — what was found, or `pending`
- **Decision** ∈ {`continue`, `shelve`, `convert-to-registration-candidate`, `n/a`}

Entries are appended in chronological order. Entries are not edited after commitment; corrections are appended as new entries referencing the prior entry's timestamp.
YYYY-MM-DDTHH:MM:SSZ  →  2026-05-25T19:30:00Z— lock-event — Charter v0.3 lock

- **Type:** `lock-event`
- **Entity:** `OMNI_Paper2_Sandbox_Charter_v0_3.docx` (lock candidate after ChatG fourth-pass review)
- **Motivation:** Charter v0.3 cleared third-pass hostile review on 25 May 2026 with no substantive remaining issues. Lock establishes the sandbox governance regime for Vector E work and the broader Paper 2 exploratory trajectory.
- **Outcome:** Charter locked; partition manifest (`holdout_manifest_v1_0.csv`) generated and SHA256 committed to GitHub `omni-geometry-mlb/paper2_sandbox/`; sentinel `sandbox_seal_v1_0.lock` placed in `CONFIRMATORY_GATE/`; event-stratum manifest (`event_stratum_manifest_v1_0.csv`) built and audited.
- **Decision:** `n/a` (governance event).

---

YYYY-MM-DDTHH:MM:SSZ  →  2026-05-25T19:30:00Z — hypothesis — PI azimuth / wave hypothesis (initial)

- **Type:** `hypothesis`
- **Entity:** *G-AZ-frame coverage compression under the PS regime structurally parallels Paper 1's bounded-G-AZ concentration regimes; the harmonic content of the RS smoothed_360 signal may transform — sharpen, simplify, or shift — under that compression. The transformation, if present, is detectable in the G-AZ frame more sensitively than in G-LON or G-RA, and is at maximum risk of artifactual misreading there.*
- **Motivation:** PI intuition formed during the ChatG hostile-review sequence on Charter v0.2 → v0.3. The hypothesis connects three existing locked observations: (i) Paper 1's bounded-G-AZ amplification mechanism (Asc 74° arc; EA 45° arc, with apparent amplification scaling inversely with arc width); (ii) the operational-scheduling confound (Charter §4.3) which compresses the apparent-azimuth distribution of PS games through start-time clustering, weather, travel, and host-city geographic concentration; (iii) Phase 1.5 spectral architecture, which is the instrument designed to measure harmonic transformation between RS and PS smoothed_360 vectors. The hypothesis is intentionally directional-agnostic: it asks whether the RS and PS regimes produce statistically distinguishable G-AZ geometries, not whether PS is "stronger."
- **Outcome:** `pending` — to be examined in Tier 1 Step 2 (per-frame occupancy diagnostics) and Tier 1 Step 4 (spectral comparison, conditional on Phase 1.5 outputs landing).
- **Decision:** `continue`.

---

YYYY-MM-DDTHH:MM:SSZ  →  2026-05-25T19:30:00Z — sequencing — Tier 1 operational sequence

- **Type:** `sequencing`
- **Entity:** Tier 1 step sequence within Charter §4.1.
- **Motivation:** Charter §4.1 declares what is admissible in Tier 1 but does not lock the order within Tier 1. Geometric diagnostics precede predictive modeling under the §6.1 modeling-philosophy commitment ("Speculative architectures last") and under ChatG third-pass guidance: characterize the RS → PS transformation geometrically before fitting models against it. Prediction-first sequencing would risk fitting a model to a transformation whose geometric structure has not yet been characterized, inflating researcher-degrees-of-freedom expenditure.
- **Outcome:** Adopted sequence within Tier 1 —
  1. **Construction.** RS/PS event-stratum manifest; BHW/GHL outcome labels; exploratory-partition loader audit; sample-balance audit across the 8-cell outcome × stratum panel.
  2. **Per-frame occupancy diagnostics.** G-AZ, G-LON, G-RA support distributions computed separately within RS and within PS; concentration-regime audit comparing the PS G-AZ arc width to the Paper 1 Asc (74°) and EA (45°) bounded arcs; coverage-tier classification per Paper 1 framework.
  3. **Unsupervised structure discovery (Vector D framing per Charter §4.2).** UMAP and clustering within RS and within PS separately, then jointly; cross-resample stability check; cross-half reproducibility check; latent-class narratives held inadmissible absent the three Vector D preconditions.
  4. **Spectral / harmonic comparison of smoothed_360 vectors across RS vs PS.** Conditional on Phase 1.5 outputs landing. Tests the harmonic-transformation component of the azimuth/wave hypothesis.
  5. **Predictive benchmarking** (calibration-led per §6.1) across logistic regression, gradient-boosted trees, and hierarchical / mixed-effects logistic alternatives. Conducted only after Steps 1–4 have characterized the geometric substrate.
- **Decision:** `continue`.

---

*(Subsequent entries appended below.)*

---

## 2026-05-25T22:30:00Z — partition-diagnostic — holdout_manifest_v1_0 generated

- **Type:** `partition-diagnostic`
- **Entity:** `holdout_manifest_v1_0.csv` — exploratory / confirmatory game-date partition (Charter §3).
- **Motivation:** First locked sandbox artifact. Establishes the 80/20 game-date partition that gates all downstream sandbox analysis under the §3 sealing protocol.
- **Outcome:** 4,760 unique game-dates across 2000–2024 (2002 absent in this per-event source despite Charter §2 retention statement; see entry below). Partition: 3,808 exploratory / 952 confirmatory dates (exactly 80.00% / 20.00%). Event-level: 46,152 exploratory / 11,483 confirmatory = 57,635 total, reconciling to the locked Paper 1 event base. Per-year balance audit confirms healthy 80/20 ratios in every year except 2020 (COVID-shortened 60-game season, expected anomaly). Manifest SHA256: `4ab6cdadcd6e5069b85f2cf60f2e6d32648998bc2b19d2afcd9e6edd2632b01c`. Sentinel `sandbox_seal_v1_0.lock` placed and loader self-test confirmed 46,152 exploratory events accessible.
- **Decision:** `continue`.

---

## 2026-05-25T22:35:00Z — partition-diagnostic — 2002 absence in per-event source

- **Type:** `partition-diagnostic`
- **Entity:** Absence of 2002 events in the canonical per-event source file (`Asc_x_MO_G-LON.csv` and presumably all per-event files in `per_event_features/`).
- **Motivation:** Charter §2 states "regular-season 2002 excluded for unavailable game start times; 2002 postseason retained." However, the per-year audit on the hold-out manifest and stratum manifest both show zero events for 2002. The per-event source therefore differs from the Charter description: the 2002 postseason appears to have been dropped during Paper 1 per-event artifact construction, not retained.
- **Outcome:** Non-blocking. The discrepancy is a documentation issue between the Charter description and the substrate data. All downstream artifacts reflect the actual data state (4,760 unique dates, 57,635 events, no 2002). The Charter description should be amended in a future revision to align with the actual per-event substrate.
- **Decision:** `continue` — flagged for Charter v0.4 amendment at next natural revision cycle.

---

## 2026-05-25T22:50:00Z — partition-diagnostic — event_stratum_manifest_v1_0 generated

- **Type:** `partition-diagnostic`
- **Entity:** `event_stratum_manifest_v1_0.csv` — RS / PS competitive-stakes-regime stratification per Charter §5.2 and Vector E (§4.3).
- **Motivation:** Tier 1 Step 1 stratification artifact. The locked Charter §5.2 schema (`event_id, stratum ∈ {regular_season, post_season}`) is the substrate for all Vector E analysis going forward.
- **Outcome:** 57,635 events classified using an authoritative per-year PS opening-date cutoff dictionary sourced from MLB.com and Wikipedia, with 2001 manually corrected to October 9 reflecting the 9/11-delayed schedule. Stratum counts: 56,779 RS / 856 PS. PS fraction 0.0149, landing inside Charter §4.3's expected ~1.5% range. Per-year RS counts ≈ 2,430 (30 teams × 162 games ÷ 2); 2020 RS at 898 reflecting the 60-game COVID-shortened season; 2002 RS at 0 per prior entry. Per-year PS counts: min 28 (2007), max 53 (2020 with 16-team expanded postseason format), mean 35.7, all within-family. Manifest SHA256: `4c02e9d7fa773ae9cae8fd0d5f7e770f311aac126292dcfa6e2cff93a1343a88`.
- **Decision:** `continue`.

---

## 2026-05-25T23:30:00Z — partition-diagnostic — outcome_labels_manifest_v1_0 generated

- **Type:** `partition-diagnostic`
- **Entity:** `outcome_labels_manifest_v1_0.csv` — per-event outcome labels for both Charter §5.1 outcome-class families (total-runs and margin-polarity).
- **Motivation:** Tier 1 Step 1 outcome-labeling artifact. Sources home/away scores and total runs from one of the cross-system master files in `MLB 2000-no0224 Training Files by System et al/` after verified date alignment between cross-system row order and per-event `event_id`.
- **Outcome:** Date alignment verified across all 57,635 events before classification (the critical safety check). Total-runs class counts: HS = 5,123 (8.89%), LS = 5,461 (9.48%), MID = 47,051. Margin-polarity class counts: BHW = 8,120 (14.09%), GHL = 7,837 (13.60%), MID = 41,678. Home-margin distribution: mean +0.121, median +1, std 4.40, range −27 to +22 — modest but real home-field advantage. Total-runs distribution: mean 9.09, std 4.54, range 1–38. Manifest SHA256: `4a7152c2eb5948b62c05095794ca36b40b68d25e12e8dd2bd3b729417afb3d31`.
- **Decision:** `continue`.

---

## 2026-05-25T23:35:00Z — hypothesis — BHW/GHL balance confirmation strengthens Vector C

- **Type:** `hypothesis`
- **Entity:** Margin-polarity tail balance vs total-runs tail balance.
- **Motivation:** PI's original premise for Vector C (Charter §4) was that BHW/GHL tails would be substantially better balanced than HS/LS tails, on the grounds that home-margin is conditioned on the home team and isolates competitive-dominance asymmetry rather than confounding offense, defense, weather, and extra innings. The outcome_labels_manifest provides the first quantitative test.
- **Outcome:** Confirmed. Margin-polarity tails (BHW 14.09%, GHL 13.60%) are nearly balanced; their slight asymmetry tracks the well-known MLB home-field advantage (mean home margin +0.12; ~54% historical home-win rate). Total-runs tails are also asymmetric in their own right (HS 8.89%, LS 9.48%) but more substantively the total-runs family puts only ~18% of events in the tails compared with ~28% for margin-polarity, giving margin-polarity nearly 1.6× the labeled-tail sample size for any given outcome-balanced contrast. This materially strengthens Vector C as a peer-level contribution rather than a side-stratification.
- **Decision:** `continue` — Vector C remains a Tier 1 priority. Promote to `convert-to-registration-candidate` candidate after Tier 1 Step 2 (per-frame occupancy diagnostics) and Step 5 (predictive benchmarking) characterize the margin-polarity signal substrate.

---

## 2026-05-25T23:40:00Z — hypothesis — PS scoring-tightening candidate observation

- **Type:** `hypothesis`
- **Entity:** *Postseason games show a noticeably tighter total-runs distribution than regular-season games: PS HS rate is 5.49% vs RS HS rate of 8.94%; PS LS rate is 11.10% vs RS LS rate of 9.45%. The postseason regime therefore appears to suppress slugfests and slightly favor pitcher's duels relative to the regular-season regime.*
- **Motivation:** This pattern surfaced incidentally during the 8-cell outcome × stratum cross-tabulation produced by the outcome-labels builder. It is consistent with the Vector E stakes-intensification hypothesis but cannot be inferentially attributed to stakes per se because all four §4.3 confounds are active: sample asymmetry (PS HS cell n = 47), calendar-window (October cold weather suppresses offense leaguewide), team-selection (PS pitchers and defenses are above-median by selection), and operational-scheduling (PS games are evening-clustered, which interacts with sky-state).
- **Outcome:** `pending`. Admissible as an architecture-discovery signal under Charter §1. Inadmissible as an inferential conclusion. Diagnostic strategy per §4.3: (i) restrict RS comparison to October-only RS games to attenuate the calendar-window confound; (ii) restrict RS comparison to games involving teams that ultimately reached the PS in their season; (iii) restrict to matched start-time bands. Implementation deferred to Tier 1 Step 2 / Step 5.
- **Decision:** `continue`.

---

## 2026-05-25T23:45:00Z — partition-diagnostic — sample-asymmetry operationalization

- **Type:** `partition-diagnostic`
- **Entity:** Vector E per-cell sample sizes in the 8-cell outcome × stratum panel.
- **Motivation:** Charter §4.3 names sample asymmetry as the first of four Vector E confounds. The outcome_labels_manifest now makes the actual PS-cell sample sizes visible for the first time.
- **Outcome:** PS-cell counts are: HS × PS = 47, LS × PS = 95, BHW × PS = 115, GHL × PS = 107. The HS × PS cell at n = 47 is the operational binding constraint. All Vector E analyses from this point forward must employ Charter §4.3's specified machinery (bootstrap effect-size confidence intervals) rather than point-estimate-only comparisons across cells of these sizes. Null-against-uniform tests calibrated for large samples are inappropriate.
- **Decision:** `continue` — incorporated as a binding methodological constraint on all subsequent Tier 1 and Tier 2 Vector E work.

---

## 2026-05-25T23:50:00Z — sequencing — protocol-discipline lesson on engine convention reuse

- **Type:** `sequencing`
- **Entity:** Date parsing in the outcome-labels builder.
- **Motivation:** During construction of `build_outcome_labels_manifest.py` an ad hoc multi-format date parser was drafted, which failed on a third date format (`5/19/2021 0:00`) embedded in the cross-system source. The Paper 1 engine (`cell_v2_batch_v2_0_2_clean.py`, function `load_feature`) had already solved this exact problem with a locked one-line pattern using `pd.to_datetime(..., errors="coerce", format="mixed")`. The ad hoc parser was discarded and the engine convention was restored.
- **Outcome:** Lesson logged. The OMNI engine encodes hard-won handling of edge cases in the source data; ad hoc reimplementation in sandbox code that touches the same substrate accumulates avoidable risk. Going forward, any sandbox cell that touches data the engine touches should default to the engine's locked patterns for date parsing, event_id construction, baseline rate computation, year extraction, and degree quantization, and deviate only with explicit rationale.
- **Decision:** `continue` — adopted as a sandbox coding standard.

---

## 2026-05-25T23:55:00Z — lock-event — Tier 1 Step 1 milestone

- **Type:** `lock-event`
- **Entity:** Three foundational sandbox manifests + ChatG concurrence on milestone closure.
- **Motivation:** With the holdout manifest, RS/PS stratum manifest, and outcome-labels manifest all locked and hashed to GitHub, the 8-cell outcome × stratum panel of Charter §5.2 is fully operational and the substrate for all subsequent Tier 1 Step 2–Step 5 work is in place. Concurrence with ChatG on milestone closure was sought and obtained.
- **Outcome:** Tier 1 Step 1 closed. Foundational manifest set: `holdout_manifest_v1_0.csv` (SHA256 `4ab6cdad…`), `event_stratum_manifest_v1_0.csv` (SHA256 `4c02e9d7…`), `outcome_labels_manifest_v1_0.csv` (SHA256 `4a7152c2…`).
- **Decision:** `n/a` (governance event). Proceeding to Tier 1 Step 2: per-frame occupancy diagnostics, G-AZ priority.

---
---

## 2026-05-26T19:00:00Z — sequencing — Step 2b closed; pivot to local conditional-rate framework

- **Type:** `sequencing`
- **Entity:** Closure of Tier 1 Step 2b (population-level circular-distribution comparison) and pivot of the Tier 1 Step 2 / Step 5 framework to local conditional-rate analysis.
- **Motivation:** Step 2b was constructed around chi-square / permutation / bootstrap circular two-sample tests answering the question "do HS and LS (or BHW and GHL) occupy globally different angular distributions?" Empirical results on Asc × MO and PI re-grounding established that this is a secondary question for OMNI. The core operational question is local conditional discrimination: under near-identical sky geometry (same-day, same-park games differing by 1–2° in feature value), does the local conditional outcome surface change rapidly enough that small angular shifts correspond to materially different outcome probabilities? Population-level distributional tests do not address this; they answer a different question, and binning-based tests at 10° / 30° resolution are structurally blind to the 1°-scale variation that matters operationally.
- **Outcome (Step 2b findings retained as established):**
    1. Asc × MO shows no globally distinguishable HS vs LS or BHW vs GHL distributions in any of G-AZ, G-LON, G-RA frames, in any of all-exploratory / RS / PS strata. All 18 permutation p-values fell between 0.31 and 0.97.
    2. G-AZ frame has a strong frame-intrinsic axial baseline: axial R̄ ≈ 0.32–0.34 across all outcome × stratum cells. The baseline is shared between HS and LS and between BHW and GHL within ≈ 0.02. This is a horizon-relative geometric effect — celestial bodies linger at East and West azimuths because azimuthal angular velocity is slowest near the horizon and fastest near transit — not an outcome-conditioned signal. Any future G-AZ outcome analysis must subtract or otherwise account for this baseline before claiming an outcome effect.
    3. The chi-square + bootstrap apparatus exhibits known sparse-bin instability at PS sample sizes (n ≤ 200), producing upward-biased Cramer's V confidence intervals. Permutation p-values remain trustworthy because both observed and permuted statistics share the bias; effect-size estimates do not.
- **Framework pivot:** The Step 2 architecture is re-centered on Paper 1's lift framework, extended into Paper 2's outcome contrasts (BHW vs GHL alongside HS vs LS) and stratification axis (RS vs PS). Step 2c is the operational continuation. The core instruments are smoothed conditional rates P(outcome | d), lift curves Lift(d) = P(outcome | d) / baseline rate, local gradient dP/dθ as the same-day discrimination metric, and engine-protocol coverage weighting via smoothed_count. Watson U², KDE-based total variation distance, and adaptive-binning chi-square corrections are not adopted; they were off-center for OMNI's operational question.
- **Decision:** `continue` — Step 2b closed; Step 2c is the immediate next deliverable. No further work on the population-distribution apparatus. Step 2c v1 will be deliberately minimal and directly continuous with the Paper 1 engine.

---
