# OMNI Paper-2 — Feature-Universe Catalog: Reproducibility Manifest
Frozen: 2026-06-18T18:33:04Z

## Provenance (verified June 2026)
Repo: github.com/crcatcrc/omni-geometry-mlb (private) -> paper2_sandbox/ | OSF: osf.io/yhxt4
Sandbox: /content/drive/MyDrive/OMNI_PROJECT/paper2_sandbox
Raw matrices: /content/drive/MyDrive/MLB 2000-no0224 Training Files by System et al
Env: Colab py3.12, numpy 2.0.2, pandas 2.2.2, sklearn 1.6.1 | Seed: 20260615

## Build chain
v1.3 enriched registry (2,494; flags+evidence)
 -> v1.5 characterization (2,494x710; coverage-validity SEPARATE from characterization-depth)
 -> v1.6 decision view (2,494x77; engine pool, rep-dev pool, HS/LS fore, BHW/GHL paused)
 -> v1.7 universes: A=345 Tier-A baseline | B=423 Tier A+B+C (A nested in B; B\A = 78 increment) | C=510 rep-dev

## Verified invariants
933 characterized = B(423)+C(510) | pool 423 = 102 rich +91 partial +230 light | pool by tier = 345 A +51 B +27 C
A ⊂ B | B ∩ C = ∅ | safe_for_direct_predictive_claim = False for all rows

## Guardrails into modeling
Sealed holdout (952 dates) never opened | in-sample lift != predictive (0.80->0.53 was leakage); GroupKFold OOF gates selection
"coverage-clean" = Tier A ∪ rotationally-supported Tier B/C; Tier B/C enter as a TESTED nested increment, not naive inclusion
BHW/GHL paused (~0.49 OOF); HS/LS is the live pole | no new methodology without PI sign-off

Per-artifact SHA-256 in REPRODUCIBILITY_MANIFEST_v1_0.csv.
