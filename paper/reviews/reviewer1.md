# Reviewer 1 (verbatim; received 2026-08-11, submission 2650209c)

The paper addresses an important problem at the intersection of machine learning and medicine.
I recommend publication after revision, pending the comments below. Point 1 in particular should
be resolved before acceptance.

1. The rounding rule retains at least one feature no matter how aggressive the cut. The
most-harmed datasets (mammographic, Haberman) are precisely those where 25% collapses to a
single feature, while the "safe" datasets retain 8–11. The paper interprets this as "datasets
with more candidate features are reliably safer to reduce" (Spearman ρ = −0.73). But feature
count and absolute retained-k are mechanically linked through this rule, so the correlation may
substantially reflect the simpler point that "reducing to one feature is unsafe." I ask the
authors to re-relate the harm to the absolute number of retained features (or compare datasets
at matched retained-k), which would separate the two explanations and either salvage or qualify
the screening criterion.

2. Feature reduction is most common where features are many (e.g. genomic data), and the authors
concede the p≫44 regime is out of scope. I would like more discussion of the precedent for
applying feature reduction to lower-dimensional medical datasets, and an explicit statement that
the guidance does not extend to the high-dimensional regime.

3. I would like at least one worked example showing where reduction would have flipped a real
treatment decision for a patient, at a specific clinically relevant threshold (net benefit is
currently averaged over a threshold range, which obscures this). This would connect the
statistical materiality to clinical materiality.

4. I would like the full Diabetes-130 cohort analyzed, at least for the headline analysis, as
the current subsampling to 6,000 weakens external validity in exactly the small-sample regime
the paper is concerned about. The "tractability" justification feels insufficient given this is
the study's only large, real-world cohort.

5. As reproducibility is a central claim of the paper, I ask that the code repository be made
available for reviewer inspection; at present it is private and no reported number can be
verified.

Thank you for the opportunity to review this well-constructed paper.
