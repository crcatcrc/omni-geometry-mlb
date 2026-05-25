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

---

## YYYY-MM-DDTHH:MM:SSZ — lock-event — Charter v0.3 lock

- **Type:** `lock-event`
- **Entity:** `OMNI_Paper2_Sandbox_Charter_v0_3.docx` (lock candidate after ChatG fourth-pass review)
- **Motivation:** Charter v0.3 cleared third-pass hostile review on 25 May 2026 with no substantive remaining issues. Lock establishes the sandbox governance regime for Vector E work and the broader Paper 2 exploratory trajectory.
- **Outcome:** Charter locked; partition manifest (`holdout_manifest_v1_0.csv`) generated and SHA256 committed to GitHub `omni-geometry-mlb/paper2_sandbox/`; sentinel `sandbox_seal_v1_0.lock` placed in `CONFIRMATORY_GATE/`; event-stratum manifest (`event_stratum_manifest_v1_0.csv`) built and audited.
- **Decision:** `n/a` (governance event).

---

## YYYY-MM-DDTHH:MM:SSZ — hypothesis — PI azimuth / wave hypothesis (initial)

- **Type:** `hypothesis`
- **Entity:** *G-AZ-frame coverage compression under the PS regime structurally parallels Paper 1's bounded-G-AZ concentration regimes; the harmonic content of the RS smoothed_360 signal may transform — sharpen, simplify, or shift — under that compression. The transformation, if present, is detectable in the G-AZ frame more sensitively than in G-LON or G-RA, and is at maximum risk of artifactual misreading there.*
- **Motivation:** PI intuition formed during the ChatG hostile-review sequence on Charter v0.2 → v0.3. The hypothesis connects three existing locked observations: (i) Paper 1's bounded-G-AZ amplification mechanism (Asc 74° arc; EA 45° arc, with apparent amplification scaling inversely with arc width); (ii) the operational-scheduling confound (Charter §4.3) which compresses the apparent-azimuth distribution of PS games through start-time clustering, weather, travel, and host-city geographic concentration; (iii) Phase 1.5 spectral architecture, which is the instrument designed to measure harmonic transformation between RS and PS smoothed_360 vectors. The hypothesis is intentionally directional-agnostic: it asks whether the RS and PS regimes produce statistically distinguishable G-AZ geometries, not whether PS is "stronger."
- **Outcome:** `pending` — to be examined in Tier 1 Step 2 (per-frame occupancy diagnostics) and Tier 1 Step 4 (spectral comparison, conditional on Phase 1.5 outputs landing).
- **Decision:** `continue`.

---

## YYYY-MM-DDTHH:MM:SSZ — sequencing — Tier 1 operational sequence

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
