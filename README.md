# Ontario Health Causal Analysis

This repository evaluates the causal impact of a public health intervention in Ontario using quasi‑experimental methods. We apply Difference‑in‑Differences (DiD), Propensity Score Matching (PSM), and Bayesian structural time‑series (CausalImpact) to estimate how the intervention changed health outcomes relative to a control region.

## Project Overview

- **Objective**: Quantify the effect of a specified Ontario public health intervention on key outcome metrics (e.g. hospitalization rates). Provide evidence‑based insights for policymakers.
- **Data Sources**: Public health and socio‑demographic data from Statistics Canada and Ontario Open Data. Covariates from the Canadian Community Health Survey. Outcome and covariate data are stored in `data/`.
- **Methods**: Data pre‑processing in Python; matching and DiD modeling in R via the `MatchIt` and `lm` packages; Bayesian time‑series impact analysis using the `CausalImpact` package. Visualizations created in Tableau.
- **Deliverables**: R Markdown analysis (`analysis.Rmd`), cleaned datasets, a Tableau story dashboard, and a policy brief.

## Installation

1. Clone this repository.
2. Install Python dependencies (for data wrangling) using pip:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Install R packages for analysis (from an R session):

```r
install.packages(c("MatchIt", "CausalImpact", "tidyverse", "ggplot2"))
```

4. Ensure Tableau Public is installed if you wish to reproduce the interactive dashboard.

## Usage

1. Prepare data: Place raw CSV files in a `data/raw/` directory (see README in data folder for details). Use a Python notebook or script to merge and clean data as needed.
2. Run the causal analysis: Open `analysis.Rmd` in RStudio and knit it to generate the detailed statistical report and plots.
3. Explore the interactive Tableau story via the provided Public link (see the project README in the repo root).
4. The final policy brief can be found in `reports/`.

## Repository Structure

- `analysis.Rmd` – Main R Markdown file performing PSM, DiD, and CausalImpact analyses.
- `requirements.txt` – Python dependencies for data preparation.
- `README.md` – Project documentation (this file).
- `data/` – Directory for raw and processed data (not included in repo).
- `reports/` – Placeholder for PDF summary and Tableau story link.

## Notes

- This project assumes you have access to public health datasets for Ontario and a comparable control region.
- Adjust the `analysis.Rmd` script to specify the intervention date, control region, and outcome metrics.
- The code is modularized to separate data prep from analysis to facilitate testing and reproducibility.
