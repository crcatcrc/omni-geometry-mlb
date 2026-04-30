# PROJECT_SCOPE  
OMNI Geometry MLB — Scope Definition  

Copyright © 2026 Courtney Roberts Conrad. All rights reserved.

## Purpose  
This document defines the exact scope of the current research project.  

Its function is to prevent:  
- scope creep  
- unplanned expansion  
- post hoc analysis changes  

Any work outside this scope is not part of this study.

## Project Title  
OMNI Geometry MLB  

## Core Objective  
To evaluate whether planetary-geometry-derived features show statistically consistent relationships with extreme scoring outcomes in MLB games.

## Dataset  
- MLB games: 2000–2024  
- Total observations: 57,635  
- Source: locked dataset documented in dataset_manifest.csv  
- All input CSVs are SHA-256 hashed and row-aligned  
- No additions or removals allowed  

## Target Variables  
Two binary outcome classes:  
- HS (high scoring)  
- LS (low scoring)  

## Feature Scope  

### Origins (6 total)  
- Asc  
- MC  
- VX  
- EA  
- MO  
- ME  

### Bodies (17 total)  
PFff, PFdn, MO, ME, VE, SU, MA, JN, CE, VS, PA, JU, NN, SA, UR, NE, PL  

### Coordinate Frames  
- G-LON  
- G-RA  
- G-AZ  

### Feature Construction  
- Same-coordinate (3)  
- Cross-coordinate (6)  
Total = 9 per pair  

### Total Feature Space  
95 origin-target pairs  
95 × 9 × 2 = 1,710 target-evaluations  

## Analysis Structure  
- Phase A — Existence (locked)  
- Phase B — Temporal Stability (locked)  
- Phase C — Symmetry (locked)  

Forward batch = confirmatory (pre-registered)

## Rules  
- No scope changes  
- No feature changes  
- No target changes  
- No adaptive decisions  

## Exclusions  
- Angle-to-angle pairs  
- H-LON (Paper 2)  
- Hygiea, Astraea  
- Non-listed bodies  
- Non-astrological variables  

## Execution Order  
1. Asc  
2. MC  
3. VX  
4. EA  
5. MO  
6. ME  

## Summary  
This study tests whether predefined planetary-geometry features demonstrate consistent statistical relationships with extreme MLB scoring outcomes under a fixed framework.
