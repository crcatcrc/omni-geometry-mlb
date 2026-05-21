# OMNI Geometry MLB

Cross-frame angular structure analysis: a self-funded research project investigating directed angular separations between local and celestial reference points as predictors of binary outcomes in a 25-year MLB sample (2000–2024, n = 57,635 events).

Copyright © 2026 Courtney Roberts Conrad.

## Scope of this repository

This repository contains the locked analytical engine, supporting code, pre-registration documents, and reproducibility artifacts for the specific manuscript submission listed below. It is the deposited reproducibility snapshot — not the broader OMNI Geometry research program, of which this submission is one component.

## Associated publication

This repository corresponds to the manuscript currently submitted to *Royal Society Open Science*. The tagged release `v1.0-rsos-submission` corresponds to the repository state at submission.

## Engine specification

The locked analytical engine is `code/cell_v2_batch_v2_0_2_clean.py` (schema 2.0.2; SHA-256 `8f7bd1ce92426eeeedb2c3b47ff24a17a1b83a6fe52b8ab2d6a9e5a1fe07c252`). It implements per-event astronomical computation via Swiss Ephemeris, coordinate transformation across G-LON / G-RA / G-AZ, angular-separation feature construction, smoothed-lift surface generation, and the Phase 1 H1 confirmatory inference described in the manuscript.

A companion single-feature analysis engine is provided as `code/cell_v2_single_v2_0_2_clean.py`.

## Repository contents

- `code/` — Analytical engine and supporting Python modules
- `docs/` — Methodological documentation
- `figures/phase_c/` — Phase C symmetry analysis figures
- `manifest/` — Run manifests
- `prereg/` — Pre-registration documents
- `registries/` — Locked feature registries
- `experiment_log.md` — Chronological experiment record
- `requirements.txt` — Python dependencies

## Companion data archive

Phase 1 and Phase 1.5 stage outputs, surrogate distributions, batch summaries, figures, and reproducibility manifests are deposited at the Open Science Framework: https://osf.io/yhxt4/

Due to file-size and licensing considerations, certain intermediate and generated artifacts are hosted through the companion OSF archive rather than directly within this GitHub repository. The two deposits together constitute the full reproducibility package.

## License

Code in this repository (files with `.py` extension) is released under the **MIT License** (see `LICENSE`).

Data files, documentation, figures, pre-registration documents, and all other non-code content are released under the **Creative Commons Attribution 4.0 International License** (CC-BY-4.0).

Attribution requirements apply under both licenses. Users of this material must cite the associated publication once available. See `NOTICE` for additional attribution guidance.

## Contact

Courtney Roberts Conrad — Independent Researcher
Cape Canaveral, Florida, USA
