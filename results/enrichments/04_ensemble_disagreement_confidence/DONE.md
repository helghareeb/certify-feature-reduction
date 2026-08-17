# DONE — Tier 4 (ensemble-disagreement AURC): SANITY STOP (honest negative)
**Second compute node · 2026-08-13**
- Confidence = RF per-tree std (pre-calibration), 12-dataset grid, paired to Tier-1 seeds.
- 🔴 Sanity: pooled Spearman(disagreement, |p-0.5|) = -0.9909 (11,180 OOF pts; per-dataset -0.96..-0.9999).
  => NOT independent of the probability => arm cannot answer => STOP per pre-ruling; the manuscript's concession STANDS.
- vote-margin ~ monotone in mean too (same verdict); did NOT hunt a 3rd confidence (per directive). Reported at full prominence.
- Files: RESULTS_tier4.md, tier4_sanity.json, MANIFEST.sha256. No raw caches.
