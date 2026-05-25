  # OMNI Paper 2 — Exploratory Sandbox

   Governance: `OMNI_Paper2_Sandbox_Charter_v0_3_LOCKED.docx`.

   ## Status

   Charter locked. Hold-out partition generation pending in Colab.

   ## Files

   - `OMNI_Paper2_Sandbox_Charter_v0_3_LOCKED.docx` — locked governance document; ChatG hostile review v0 → v0.3 complete.
   - `generate_holdout_partition.py` — partition-generation procedure with literal seed `OMNI_P2_SEED = 20260524`. Committed to GitHub before manifest generation per Charter §3.
   - `sentinel_and_loader.py` — sentinel placement and exploratory-partition loader helper.
   - `exploration_log.md` — append-only project log per Charter §7.
   - `holdout_manifest_v1_0.sha256.txt` — SHA256 of the generated manifest (added after Colab generation).

   ## Procedure at Charter lock

   1. Commit this directory.
   2. Run `generate_holdout_partition.py` in Colab against the canonical event source.
   3. Capture printed SHA256; commit it as `holdout_manifest_v1_0.sha256.txt`.
   4. Run `sentinel_and_loader.py` in Colab.
   5. Update `exploration_log.md` with actual lock timestamps; commit.

   Confirmatory hold-out is sealed by the `sandbox_seal_v1_0.lock` sentinel under `/content/drive/MyDrive/OMNI_PROJECT/paper2_sandbox/CONFIRMATORY_GATE/` and may be opened only after the Paper 2 pre-registration is locked on OSF.
