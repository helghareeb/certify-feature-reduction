# TRIPOD+AI adherence note

This study is a *reliability audit of feature reduction*, not the development of a single deployable
clinical prediction model. We therefore map our reporting to the TRIPOD+AI items that apply to a
methodological evaluation that builds and scores many models across datasets, learners, and feature
budgets (Collins et al., BMJ 2024; doi:10.1136/bmj.q902).

| TRIPOD+AI item (theme) | Where addressed |
|---|---|
| Title / Abstract — study type, objective, methods, results | Title; structured abstract |
| Background and objectives | Introduction; pre-registered research question |
| Data sources, participants, predictors | Methods §Datasets; Table 1; `data/<name>/README.md` |
| Outcome definition | Methods §Datasets (per-dataset binary outcome) + §Outcomes |
| Sample size | Table 1 (n per dataset); Diabetes-130 subsample seed recorded |
| Missing data | In-fold median imputation under the leakage firewall (Methods) |
| Model / analysis — learners, feature ranking, budgets | Methods §Protocol; 3 learners × 3 rankers × 5 budgets |
| **Discrimination** | AUROC (Methods §Outcomes; Results) |
| **Calibration** | ECE + Brier; calibration-in-the-small via recalibration control |
| **Clinical utility** | Decision-curve net benefit (Vickers 2006); Results §Reduction costs clinical utility |
| **Uncertainty / reliability** | Selective reliability (AURC) + split-conformal coverage & set size |
| **Fairness across subgroups** | Subgroup gaps in AUROC, ECE, net benefit, conformal coverage |
| Model performance — uncertainty quantification | Holm-corrected tests + 5000-resample bootstrap CIs |
| Open science — code, data, protocol, reproducibility | Code & Data availability; pre-registration; every number regenerates from a recorded seed (R1) |
| Fairness — protected attributes, justification | Methods §Outcomes; Sex-and-gender statement; protected attrs never model features |
| Limitations | Limitations subsection; Threats folded in |

Items specific to a single deployed model (e.g. a published model equation, external temporal
validation of one model, a risk-score nomogram) are out of scope by design: the contribution is the
*auditing protocol* and its cross-dataset findings, not a model for deployment.
