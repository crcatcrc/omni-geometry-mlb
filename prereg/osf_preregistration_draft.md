# OSF Pre-Registration Draft

## Title
Confirmatory analysis of cross-frame angular structure in directed planetary geometry features as predictors of MLB scoring outcomes.

## Dataset
- MLB games: 2000–2024  
- Total observations: 57,635  
- Data locked via dataset_manifest.csv  

## Targets
- HS (high scoring)  
- LS (low scoring)  

## Feature Scope
Origins:
Asc, MC, VX, EA, MO, ME  

Bodies (17):
PFff, PFdn, MO, ME, VE, SU, MA, JN, CE, VS, PA, JU, NN, SA, UR, NE, PL  

Protocol:
- Fast → slow only  
- No reverse pairs  

Coordinate frames:
G-LON, G-RA, G-AZ  

Constructions:
- 3 same-coordinate  
- 6 cross-coordinate  

Total:
95 pairs × 9 constructions × 2 targets = 1,710 evaluations  

## Hypotheses

H1 — Structure exists  
Peak smoothed lift > 1.15 in ≥ 50% of evaluated combinations  

H2 — Temporal stability  
≥ 75% anchor classification across 7-block partitions  

H3 — Origin consistency  
Results stable across origins within ±20%  

## Method

Engine:
v2.0.2 (locked)  

Procedure:
- Phase A: structure detection  
- Phase B: temporal validation  
- No Phase C during batch  

## Rules

- No parameter changes  
- No threshold changes  
- No feature filtering  
- No adaptive decisions  

## Exclusions

- Angle-to-angle pairs  
- H-LON  
- Non-listed bodies  
- Non-astrological variables  

## Execution

Order:
Asc → MC → VX → EA → MO → ME  

All features executed  
No early stopping  

## Classification

- Phases A/B/C → exploratory  
- Forward batch → confirmatory  

## Integrity

- All data verified via SHA-256  
- All runs executed from committed code  
- All results reproducible  

## Summary

This pre-registration defines a fixed confirmatory test of planetary-geometry-derived feature structure under strict reproducibility constraints.
