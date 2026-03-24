# Sample PA Cases

5 prior authorization test cases matching the implementation spec (`.claude/plans/demo-implementation-prompt.md` §3):

1. **`01_lumbar_mri_clear_approval.json`** — Lumbar MRI for radiculopathy (M54.5/M54.41, CPT 72148). Conservative therapy documented. Expected: **APPROVED**
2. **`02_cosmetic_rhinoplasty_denial.json`** — Cosmetic rhinoplasty with diagnosis mismatch (L57.0, CPT 30400). No medical necessity. Expected: **DENIED**
3. **`03_spinal_fusion_complex_review.json`** — Lumbar spinal fusion with comorbidities (M47.816/M48.06/E11.9, CPT 22612/22614/22842). Requires specialist review. Expected: **PENDED_FOR_REVIEW**
4. **`04_humira_missing_documentation.json`** — Humira for RA, missing step therapy docs (M05.79, HCPCS J0135). Incomplete submission. Expected: **PENDED_MISSING_INFO**
5. **`05_keytruda_urgent_oncology.json`** — Keytruda for lung cancer, urgent (C34.11/C77.1, HCPCS J9271). Stage IIIA with pathology. Expected: **APPROVED**

Each case is structured as a FHIR R4 Claim resource with `use: "preauthorization"` per Da Vinci PAS IG.
