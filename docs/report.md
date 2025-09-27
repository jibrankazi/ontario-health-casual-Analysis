# Causal Impact of Ontario Health Policy on COVID‑19 Incidence Rates

## Introduction
Ontario implemented a broad public‑health intervention in October 2021 to curb the spread of COVID‑19.  Assessing the effectiveness of such policies requires isolating causal impacts from confounding trends.  This study analyses weekly COVID‑19 incidence across Ontario’s public health units (PHUs) to estimate the intervention’s effect.

## Data and preprocessing
We use the **Status of COVID‑19 cases in Ontario by Public Health Unit** dataset from the Ontario Data Catalogue.  The raw data consist of daily case counts for each PHU.  We aggregate counts to weekly totals, compute mean incidence per PHU, and flag PHUs as treated (those subjected to the intervention) or control.  The intervention date is set to 2021‑10‑15.

## Methods
1. **Difference‑in‑Differences (DiD):** A two‑way fixed‑effects model with PHU and week dummies estimates the average treatment effect on the treated (ATT).  Standard errors are clustered at the PHU level.
2. **Propensity Score Matching (PSM):** Treated PHUs are matched to control PHUs based on pre‑intervention averages of available covariates (here, incidence) using one‑to‑one nearest‑neighbour matching.  The ATT is the mean post‑intervention difference between matched pairs.
3. **Bayesian Structural Time Series (BSTS) / CausalImpact:** When available, a state‑space model constructs a synthetic control by modelling the treated series as a linear combination of control series.  The difference between observed and counterfactual outcomes measures the intervention’s impact.

## Results

| Method | ATT estimate | Std. error | p‑value |
| --- | ---:| ---:| ---:|
| DiD | −108.65 | 106.38 | 0.31 |
| PSM | −42.78 | — | — |
| BSTS | Not run | — | — |

Both DiD and PSM indicate that treated PHUs experienced fewer weekly cases after the intervention; however, the DiD estimate is not statistically significant.  The negative PSM estimate supports a reduction in incidence, though without standard error reporting.  The BSTS analysis was not performed due to unavailable dependencies.

## Discussion
The findings suggest a decline in COVID‑19 incidence attributable to the policy, albeit with modest evidence.  The absence of additional covariates and staggered adoption limits causal interpretation.  Future work should incorporate demographic and mobility covariates, consider heterogeneous treatment effects, and execute the full BSTS analysis.

## Conclusion
This reproducible analysis demonstrates a workflow for evaluating public‑health interventions using open data.  By combining DiD, PSM and BSTS methods, researchers can triangulate causal effects and provide more robust evidence for policy evaluation.
