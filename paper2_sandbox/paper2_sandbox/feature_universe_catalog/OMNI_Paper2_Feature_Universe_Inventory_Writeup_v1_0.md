# Reconciling and Cataloguing the Aspect-Feature Universe for OMNI Paper 2: A Coverage-Aware Candidate-Selection Framework

**Project:** OMNI Paper 2 — Horizontal-systems geometric prediction of MLB outcomes
**Phase:** Feature-Universe Inventory (registry chain v1.3 → v1.7, with reproducibility freeze)
**Status:** Complete and frozen; modeling phase pending
**Environment of record:** Google Colab, Python 3.12, numpy 2.0.2, pandas 2.2.2, scikit-learn 1.6.1
**Global random seed:** 20260615
**Repository:** `github.com/crcatcrc/omni-geometry-mlb` (private) → `paper2_sandbox/` · **OSF:** `osf.io/yhxt4`

---

## Abstract

This phase reconciled the full aspect-feature universe underlying OMNI Paper 2 and converted it into a single, coverage-aware, candidate-selection catalogue suitable for disciplined predictive modeling. We established that the feature universe comprises **2,494** geometric aspect features distributed across **16** coordinate-system-pair matrices, of which only an H-LON-adjacent corner had been carried into prior machine-learning work. Through a four-stage registry chain (v1.3 → v1.5 → v1.6 → v1.7), we (i) attached all extant analytical evidence to every feature, (ii) separated *coverage validity* from *characterization depth* as orthogonal axes, (iii) preserved the outcome-pole structure of the evidence rather than averaging it away, and (iv) emitted three reproducible modeling universes. The central empirical result is a quantification of Paper 1's coverage-regime prediction: of the **209** richly characterized features, only **102** are coverage-clean while **107** ride on degenerate sampling geometry — a near-even split that converts a previously conceptual argument into a measured property of the catalogue. The honest first-pass candidate universe is **423** characterized, coverage-clean features; a parallel **510**-feature pool is reserved for representation-development. The complete chain is hash-verified end-to-end and archived with per-artifact SHA-256 provenance. Throughout, the sealed confirmatory holdout was never accessed, and every catalogue field is explicitly flagged as descriptor-inventory evidence requiring fold-clean out-of-sample validation before any predictive claim.

---

## 1. Background and motivation

### 1.1 The scope problem

OMNI Paper 2 extends the project's geometric-prediction program from a small, well-studied set of heliocentric-longitude (H-LON) targets to the broader space of aspect features available across the project's coordinate systems. Prior modeling and exploratory work, including Phase 3A, operated on an H-LON-adjacent slice of features (H-LON × H-LON and geocentric-origin × H-LON pairs). A recurring uncertainty was whether that slice represented the feature universe or merely one corner of it.

The Feature-Universe Reconciliation established the latter. The canonical universe is **2,494** aspect features spanning **16** coordinate-system-pair matrices built from four frames — geocentric azimuth (G-AZ), geocentric longitude (G-LON), geocentric right ascension (G-RA), and heliocentric longitude (H-LON) — in both same-system and cross-system configurations. The feature universe is therefore distinct from, and substantially larger than, the *analyzed* universe inherited from earlier phases. Modeling against an undocumented subset risked silent selection effects and non-reproducible candidate lists; the inventory phase exists to remove that risk before any model is fit.

### 1.2 Antecedent: the Paper 1 coverage-regime framework

Paper 1 (§4.6–4.9) argued that the *depth* of analytical evidence for a feature is not the same as its *fitness for modeling*, because much of the project's geometry is sampled under degenerate conditions. Inner bodies (Mercury, Venus, Sun) are constrained in apparent motion relative to certain frames; outer bodies (Uranus, Neptune, Pluto) are sparsely covered over the observation window; and several frame configurations are rotationally or solar-locked. Paper 1 predicted, qualitatively, that a meaningful fraction of the deepest evidence would prove to rest on such regimes. Paper 1 (§4.11) further outlined coverage-aware modeling strategies — coverage-weighted estimation, hierarchical pooling across frames, and body × frame interaction terms — that the project's flat sin/cos logistic baselines had never applied. The inventory phase was designed to make the §4.6–4.9 prediction measurable and to produce a catalogue against which the §4.11 strategies could be targeted.

---

## 2. Design principles

Four principles governed every stage of the registry chain.

**Coverage validity is orthogonal to characterization depth.** A feature can be richly analyzed yet sit on degenerate geometry, or sparsely analyzed yet cleanly sampled. Collapsing these into a single "quality" score would reintroduce exactly the confound Paper 1 warned against. The catalogue therefore carries each as an independent column, and candidate eligibility is defined on their joint.

**Retain-and-flag, never discard.** Features outside current modeling scope — H-LON-origin features not yet analyzed, or coverage-compromised features — are retained in the catalogue with an explicit exclusion or deferral flag, never dropped. Absence of evidence is recorded as such and is distinguished from negative evidence.

**In-sample descriptor evidence is not predictive worth.** Every evidence field in the catalogue (support, peak lift, persistence, topology) is in-sample characterization. The project has already observed an in-sample degree-response library run AUC ≈ 0.80 against a fold-clean truth of ≈ 0.53; that 0.27 gap was target-encoding leakage. The catalogue accordingly stamps every row as descriptor-only and requiring fold-clean out-of-sample (OOF) validation before any keep/cut decision.

**The confirmatory holdout is sealed.** A confirmatory partition of **952** dates is reserved and was never accessed during this phase. All inventory work is exploratory by construction; the holdout's credibility depends on its never having informed catalogue or candidate decisions.

---

## 3. Methods: the registry chain

The chain transforms an enriched per-feature registry into three modeling-ready candidate universes through four deterministic, QA-gated stages. No stage performs a new data merge beyond the documented evidence joins in v1.5; v1.6 and v1.7 are deterministic views of their inputs.

### 3.1 Input — v1.3 enriched analysis registry

`MASTER_ASPECT_FEATURE_ANALYSIS_REGISTRY_v1_3.csv` (2,494 rows) carries, for every feature, both presence flags and evidence values from each upstream analysis layer. Eight analysis layers contribute, with fixed expected feature counts used as join checksums throughout the chain:

| Layer | Expected features | Source |
|---|---|---|
| Paper 1 (HS/LS degree-response) | 741 | omni feature registry (1,482 = 741 × 2 poles) |
| Phase 1.5 | 6 | phase1p5 |
| FSA operational-scale | 241 | feature-scale-analysis / operational-scale registry |
| H-LON descriptor | 192 | Phase 2B-1 heliocentric horizontal engine |
| Step 2c | 209 | step2c conditional metrics |
| Operating-point | 209 | operating-point metrics |
| Engineering-priority | 18 | priority registry |
| Phase 3c (HIGH/AVG/LOW response) | 192 | phase3c response summary |

These eight totals are asserted exactly at each join. A reproduced count that does not match signals a broken merge — most often an un-canonicalized `feature_id` (the project's registries were built at different times and use varying `×`/`x`, body-abbreviation, and origin-target-ordering conventions). Feature identifiers are canonicalized before any join so that a feature characterized in one layer is never silently mislabeled "unanalyzed" in another.

### 3.2 v1.5 — Characterization registry (three-axis catalogue)

`build_characterization_registry_v1_5.py` converts the enriched registry into a 2,494 × 710 characterization table. It attaches the underlying evidence values (239 metric/evidence columns detected) and derives three independent classifications.

*Characterization depth* is assigned from the number of analysis layers present, partitioning the universe as follows:

| Status | Features | Layer rule |
|---|---|---|
| Richly characterized | 209 | 4–5 layers (185 at 4, 24 at 5) |
| Partially characterized | 224 | 2 layers |
| Lightly characterized | 500 | 1 layer |
| Unanalyzed (in scope) | 1,320 | 0 layers, in scope |
| Excluded (H-LON-origin, not analyzed) | 241 | 0 layers, out of scope |
| **Total** | **2,494** | |

*Coverage validity* is derived from coverage tier and operational-scale class, with the observed tier vocabulary:

| Coverage tier | Features |
|---|---|
| Tier A | 787 |
| Sparse-coverage | 768 |
| Tier B | 356 |
| Constrained-motion | 229 |
| Tier C | 224 |
| Part of Fortune | 54 |
| (nan) | 50 |
| Earth/solar-locked | 26 |

*Outcome pole* is preserved rather than averaged: HS/LS (and BHW/GHL, and the Phase 3c HIGH/AVG/LOW poles) are stored as distinct fields, because peak degree and lift differ by pole. 933 features carry outcome-pole fields — exactly the characterized universe (209 + 224 + 500), confirming that pole-evidence coverage equals characterization coverage.

**Guards (v1.5).** Two defensive checks were added after audit, each targeting a silent-mislabel mode: (i) a required-column guard asserting that scope and tier columns exist before any row-wise classifier runs — absent them, `row.get(...)` would return `None` and every feature would fall to a default class while the cell ran clean; (ii) a tier-vocabulary reconciliation that prints the true tier tokens and asserts that fewer than half the universe falls to `coverage_unclassified`, catching the case where the classifier's match-strings do not match the registry's actual tokens. Scope resolved cleanly to 2,253 in-scope / 241 excluded; only the 50 genuine `nan`-tier features remained unclassified, confirming the coverage axis populated rather than collapsed. End-to-end integrity reconciled: the v1.4 "1,561 zero-layer" features resolved exactly into 241 excluded + 1,320 in-scope-unanalyzed, and the 241 excluded distributed across tiers (≈ 60 Tier-A, ≈ 108 quarantine-class, ≈ 73 Tier-B/C) without double-counting against the scope axis.

### 3.3 Joint status check — the candidate-pool finding

`joint_status_check_v1_5.py` crosses characterization depth against coverage validity. "Coverage-clean" is defined as the union `{coverage_clean, coverage_clean_or_rotationally_supported}`; the quarantine classes (Sparse-coverage, Constrained-motion, Earth/solar-locked, Part of Fortune, and `nan`) are excluded from clean. The joint over the 933 characterized features is:

| Coverage-clean? | Rich | Partial | Light | Total |
|---|---|---|---|---|
| **Yes** | 102 | 91 | 230 | **423** |
| **No** | 107 | 133 | 270 | **510** |
| **Total** | 209 | 224 | 500 | 933 |

This table is the load-bearing scientific output of the inventory (§7).

### 3.4 v1.6 — Decision view

`build_decision_view_v1_6.py` reduces the 710-column registry to a 2,494 × 77 analyst-facing table: identity, geometry, coverage validity, characterization status, layer flags, foregrounded HS/LS evidence (peak degree, peak smoothed-lift, support per pole), carried-but-paused BHW/GHL evidence, FSA operational fields, and three derived decision flags. The engine-candidate pool is defined transparently and structurally — no in-sample lift threshold is baked in:

```
engine_candidate_pool = is_characterized
                        AND coverage_validity_class ∈ {clean, clean_or_rotationally_supported}
                        AND analysis_scope_flag == "in_scope"
```

The representation-development pool is its complement on the not-clean side (`is_characterized AND NOT clean AND in_scope`). Each row carries `descriptor_evidence_only = True`, `requires_oof_validation_before_candidate_selection = True`, and `safe_for_direct_predictive_claim = False`, embedding the in-sample≠predictive guardrail directly in the table. A provenance stamp (input SHA-256, seed, UTC timestamp) is written to every row.

**Guards (v1.6).** Three checks were added after audit. (A) A **column-resolution map** prints the v1.5 column each evidence term-set resolved to, and asserts that the core HS/LS evidence columns resolved to non-empty names and are populated on their layer subset — without this, the dynamic column-matching could silently blank the entire evidence payload while QA passed. The map confirmed, e.g., `paper1_HS_peak_lift → paper1_HS_peak_smoothed_lift`, populated on 741/741 Paper 1 rows. (B) The eight **layer-total checksums** were added to QA, reproducing 741/6/241/192/209/209/18/192 after Boolean coercion. (C) The Boolean coercion routine was hardened to handle numeric truthy values (e.g., float `1.0`), since a column read back as float would otherwise collapse silently to all-`False`. Checks (B) and (C) interlock: a coercion failure would surface as a layer-total mismatch.

### 3.5 Tier-composition audit

`tier_composition_audit_v1_6.py` surfaces the coverage-tier composition of the 423-feature engine pool, which the strength tiers (which rank characterization depth) do not expose. Because "coverage-clean" admits rotationally-supported Tier B/C, the pool is not Tier-A-exclusive:

| Coverage tier | Rich | Partial | Light | Total |
|---|---|---|---|---|
| Tier A | 90 | 85 | 170 | 345 |
| Tier B | 8 | 3 | 40 | 51 |
| Tier C | 4 | 3 | 20 | 27 |
| **Total** | 102 | 91 | 230 | **423** |

The pool is 82% Tier A (345); Tier B/C contribute 78 features, concentrated in the lightly characterized cell (60 of 78). This audit converted an implicit definitional choice — whether Tier B/C belong in first-pass modeling — into an explicit decision for the PI (§8.1).

### 3.6 v1.7 — Modeling universe manifests

`build_universe_manifests_v1_7.py` emits three reproducible candidate universes as deterministic subsets of v1.6 (no new join), each provenance-stamped and sorted by candidate-strength rank:

| Universe | Definition | n | Modeling role |
|---|---|---|---|
| **A** | engine pool ∩ Tier A | 345 | Strict first-pass baseline |
| **B** | engine pool (Tier A+B+C) | 423 | Expanded first-pass; A strictly nested in B |
| **C** | representation-development pool | 510 | Not first-pass input |

Universe A is strictly nested in Universe B, so the 78 Tier-B/C features constitute a clean nested increment over the baseline. Universe C is disjoint from B. The representation-development pool decomposes by deferral reason into 414 quarantine-or-special-handling and 96 coverage-conditional features.

---

## 4. Quality assurance and reproducibility

### 4.1 Fail-loud QA gates

Every build stage raises before writing any output if any check fails. The v1.7 gate (15 checks, all passed) asserts cardinality (A = 345, B = 423, C = 510), uniqueness of `feature_id` within each manifest, the set relations A ⊂ B and B ∩ C = ∅, the closure identity |B| + |C| = 933, the tier decomposition of B (345/51/27), and — as a standing guardrail — that the count of rows asserting a direct predictive claim is **0** in every manifest.

### 4.2 Hash-verified chain of custody

The reproducibility freeze (`REPRODUCIBILITY_MANIFEST_v1_0.csv`, `REPRODUCIBILITY_README.md`) hashes every canonical artifact from disk and cross-checks the chain. The v1.5 file hashes to the exact input SHA stamped by the v1.6 build, and the v1.6 file hashes to the exact input SHA stamped by the v1.7 manifests, so v1.3 → v1.5 → v1.6 → v1.7 is a verified chain rather than an asserted one. The freeze fails loud if any canonical artifact is absent, directly preventing the omission failure that has cost project time previously.

### 4.3 Provenance anchors (verified June 2026)

| Anchor | Value |
|---|---|
| Repository | `github.com/crcatcrc/omni-geometry-mlb` (private) → `paper2_sandbox/` |
| OSF | `osf.io/yhxt4` |
| Sandbox (OUTDIR) | `/content/drive/MyDrive/OMNI_PROJECT/paper2_sandbox` |
| Raw aspect matrices | `/content/drive/MyDrive/MLB 2000-no0224 Training Files by System et al` |
| Environment | Colab, Python 3.12, numpy 2.0.2, pandas 2.2.2, sklearn 1.6.1 |
| Seed | 20260615 |

Repository and OSF were verified against Paper 1's code- and data-accessibility sections; both Drive paths were verified against `phase3a_analysis.py`, the Phase 2B-1 runner, and the modeling handoff.

---

## 5. Results

The principal results are the partition of the 2,494-feature universe (§3.2), the joint candidate-pool table (§3.3), the tier composition of the engine pool (§3.5), and the three modeling universes (§3.6). In summary:

- The universe partitions into 209 richly / 224 partially / 500 lightly characterized features, plus 1,320 in-scope-unanalyzed and 241 excluded H-LON-origin features.
- The honest first-pass candidate universe is **423** characterized, coverage-clean features (102 rich + 91 partial + 230 light), of which 345 are Tier A and 78 are rotationally-supported Tier B/C.
- A reserved **510**-feature representation-development pool holds characterized but coverage-compromised features.
- Of the 209 richly characterized features, **102** are coverage-clean and **107** are not — the quantified quarantine result (§7).

---

## 6. Artifacts and data availability

All artifacts reside in `paper2_sandbox/` and are mirrored to the repository with per-file SHA-256 recorded in `REPRODUCIBILITY_MANIFEST_v1_0.csv`.

| Artifact | Rows | SHA-256 (prefix) |
|---|---|---|
| `MASTER_ASPECT_FEATURE_ANALYSIS_REGISTRY_v1_3.csv` | 2,494 | `939b6a33…` |
| `MASTER_ASPECT_FEATURE_CHARACTERIZATION_REGISTRY_v1_5.csv` | 2,494 | `0c4b05f1…` |
| `MASTER_ASPECT_FEATURE_CHARACTERIZATION_REGISTRY_QA_v1_5.csv` | 10 | `09d1ef81…` |
| `MASTER_ASPECT_FEATURE_CHARACTERIZATION_REGISTRY_SUMMARY_v1_5.txt` | — | `af6ff141…` |
| `MASTER_ASPECT_FEATURE_DECISION_VIEW_v1_6.csv` | 2,494 | `f54f4976…` |
| `MASTER_ASPECT_FEATURE_DECISION_VIEW_QA_v1_6.csv` | 16 | `598f315b…` |
| `MASTER_ASPECT_FEATURE_DECISION_VIEW_SUMMARY_v1_6.txt` | — | `7713160a…` |
| `HS_LS_UNIVERSE_A_TIER_A_ENGINE_MANIFEST_v1_7.csv` | 345 | `572716bd…` |
| `HS_LS_UNIVERSE_B_TIER_ABC_ENGINE_MANIFEST_v1_7.csv` | 423 | `154c0925…` |
| `HS_LS_UNIVERSE_C_REPRESENTATION_DEVELOPMENT_MANIFEST_v1_7.csv` | 510 | `b4befe89…` |
| `HS_LS_MODELING_UNIVERSE_MANIFESTS_QA_v1_7.csv` | 15 | `07dd54df…` |
| `HS_LS_MODELING_UNIVERSE_MANIFESTS_SUMMARY_v1_7.txt` | — | `9480fe4f…` |

**Build scripts** (archived verbatim): `build_characterization_registry_v1_5.py`, `joint_status_check_v1_5.py`, `build_decision_view_v1_6.py`, `tier_composition_audit_v1_6.py`, `build_universe_manifests_v1_7.py`. Each registry CSV is reproducible by running its script against the SHA-named input under the seed and environment of record.

---

## 7. Interpretation and scientific significance

The catalogue's central result is the quantification of Paper 1's coverage-regime prediction. The §4.6–4.9 argument — that much of the project's deepest evidence rests on degenerate sampling — was, until this phase, conceptual. The joint table makes it measurable: of the 209 richly characterized features, 102 are coverage-clean and 107 are not, a near-even split. Roughly half of the project's most heavily analyzed geometry sits on Sparse-coverage outer bodies, Constrained-motion inner bodies, or solar-locked / Part-of-Fortune configurations.

Two interpretive cautions bound this result. First, the table establishes the **structural** form of the prediction — that rich evidence co-occurs with coverage compromise — and not its **consequence**. Whether the 107 features' descriptor signals are actually inflated by their sampling geometry is a separate question that only fold-clean OOF testing can answer; co-occurrence of richness and compromise is not demonstrated degradation. Second, the 107 features are not discarded. They are reserved as representation-development candidates — for phase-folding, motion-matched encoding, and coverage-normalized transforms — and are the natural locus of any future Paper-3-type methodological contribution.

More broadly, the inventory replaces ad hoc feature lists with a single audited object in which coverage validity and characterization depth are first-class, separable, and jointly queryable. Every subsequent modeling result becomes interpretable against a fixed, documented candidate universe rather than an implicit one.

---

## 8. Decisions and rationale

### 8.1 Tier B/C enter as a tested nested increment

The engine pool's "coverage-clean" definition admits rotationally-supported Tier B/C features, which Paper 1's framing had treated as coverage-conditional. Rather than resolve their eligibility on theory, the PI directed that they be tested empirically: in-model performance is the only definitive verdict on whether a feature contributes, and freezing Tier B/C out a priori would foreclose the question. The three-universe design operationalizes this without mixing tiers invisibly. Because Universe A is strictly nested in Universe B, the comparison is a nested increment: the same model, fitted under identical date-grouped (GroupKFold) splits, seed, and pipeline on A and on A+B+C, attributes any AUC change to the 78 Tier-B/C features alone. The increment is to be reported with a standard error, not as a bare point difference, since a delta of the magnitude seen for the geometry increment in prior work (≈ +0.01) is within noise absent a small SE.

### 8.2 HS/LS is the live pole; BHW/GHL is paused

The decision view foregrounds HS/LS evidence and carries BHW/GHL fields marked as a paused margin track. The BHW/GHL margin family tested at chance (OOF ≈ 0.49) in prior work; its evidence is retained for completeness but is never treated as co-equal and must not re-enter candidate selection silently.

---

## 9. Limitations and caveats

The catalogue records in-sample descriptor evidence only; it makes no predictive claim, and the `safe_for_direct_predictive_claim = False` stamp on every row is load-bearing, not decorative. The FSA operational class carried into the catalogue is provisional (`fsa_operational_class_provisional`); any downstream use inherits that status. The Paper 1 lift fields are **smoothed** lift summarized per feature — appropriate as catalogue evidence, but to be kept distinct from per-event smoothed-lift recomputed on full data, which is a target-derived leakage vector and must be recomputed fold-clean if used as a model input. "Coverage-clean" throughout denotes the union of strictly clean and rotationally-supported geometry, and is broader than strictly clean; the tier composition (§3.5) is the disambiguating record. Finally, coverage-clean-but-unanalyzed features (the 1,320 in-scope-unanalyzed) are absent-evidence, not non-features; the 423 is the descriptor-candidate pool, not the ceiling of the eventually model-valid universe.

---

## 10. Forward plan

The inventory is complete; discovery now yields to model construction. The staged plan is: (i) assemble the coverage-clean per-event panel as the engine's design matrix, restricted to Universe A, over the project's pre-registered origins (Ascendant, Midheaven, Vertex, Earth, Moon, Mercury) × frames; (ii) fit a baseball-first baseline; (iii) add geometry as a leakage-controlled increment under date-grouped OOF; (iv) test the Universe A → A+B+C nested increment to decide Tier B/C empirically; and (v) apply the Paper 1 §4.11 coverage-aware strategies — coverage weighting, hierarchical pooling across frames, body × frame interactions — that the flat baselines never used. The 510-feature representation-development pool is reserved for later coverage-normalized and motion-matched representations. First-pass modeling opens in a fresh thread seeded by this record. The confirmatory holdout of 952 dates remains sealed and is not to be accessed until pre-registered abstention rules and the increment protocol are frozen on exploratory data.

---

## Appendix A — Reproduced layer-total checksums

Paper 1 = 741 · Phase 1.5 = 6 · FSA = 241 · H-LON = 192 · Step 2c = 209 · Operating-point = 209 · Priority = 18 · Phase 3c = 192. All reproduced exactly at every join in v1.3 → v1.5 and re-asserted in the v1.6 QA gate after Boolean coercion.

## Appendix B — Closure identities (all QA-verified)

- Characterization partition: 209 + 224 + 500 + 1,320 + 241 = 2,494
- Characterized universe: 209 + 224 + 500 = 933 = |B| (423) + |C| (510)
- Engine pool by depth: 102 + 91 + 230 = 423
- Engine pool by tier: 345 + 51 + 27 = 423
- Representation-development by reason: 414 + 96 = 510
- Set relations: A ⊂ B; B ∩ C = ∅
- Predictive-claim rows in every manifest: 0

## Appendix C — Glossary of frames and selected bodies

Frames: G-AZ (geocentric azimuth), G-LON (geocentric longitude), G-RA (geocentric right ascension), H-LON (heliocentric longitude). Coverage regimes: Constrained-motion (inner bodies — Mercury, Venus, Sun — restricted in apparent motion); Sparse-coverage (outer bodies — Uranus, Neptune, Pluto — sparsely sampled over the window); Earth/solar-locked and Part of Fortune (geometrically degenerate configurations). Outcome poles: HS/LS (high-scoring / low-scoring, the live target), BHW/GHL (paused margin family), and the Phase 3c HIGH/AVG/LOW response classes.
