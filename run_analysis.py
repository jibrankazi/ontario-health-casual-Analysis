import json, warnings, yaml, pathlib
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from statsmodels.formula.api import ols
import statsmodels.api as sm

warnings.filterwarnings("ignore")

# ---------- load config ----------
cfg = yaml.safe_load(open("config.yaml"))
DATA = pathlib.Path(cfg["data_path"])

date_col   = cfg["date_col"]
unit_col   = cfg["unit_col"]
y_col      = cfg["outcome_col"]
treat_col  = cfg["treat_col"]
covs       = cfg.get("covariates", [])
t0         = pd.to_datetime(cfg["intervention_date"])
freq       = cfg.get("freq", "W")

# ---------- load data ----------
df = pd.read_csv(DATA)
df[date_col] = pd.to_datetime(df[date_col])
df = df.sort_values([unit_col, date_col]).copy()

# sanity
need = {date_col, unit_col, y_col, treat_col}
missing = need - set(df.columns)
if missing:
    raise SystemExit(f"Missing required columns in {DATA}: {missing}")

# ---------- pre/post indicators ----------
df["post"] = (df[date_col] >= t0).astype(int)
df["tp"] = df[treat_col]*df["post"]

# ---------- event-study style plot (means by group) ----------
g = df.groupby([date_col, treat_col])[y_col].mean().reset_index()
fig1 = plt.figure()
for grp, lab in [(1, "Treated"), (0, "Control")]:
    sub = g[g[treat_col]==grp]
    plt.plot(sub[date_col], sub[y_col], label=lab)
plt.axvline(t0, linestyle="--", color="k")
plt.legend(); plt.title("Outcome by group over time (mean)"); plt.tight_layout()
pathlib.Path("figures").mkdir(exist_ok=True)
plt.savefig("figures/fig1_event_trends.png", dpi=150); plt.close()

# ---------- DiD (two-way FE via dummies) ----------
# y ~ treated*post + unit FE + time FE + covariates
formula = f"{y_col} ~ tp + C({unit_col}) + C({date_col})"
if covs:
    formula = f"{y_col} ~ tp + " + " + ".join(covs) + f" + C({unit_col}) + C({date_col})"
did = ols(formula, data=df).fit(cov_type="cluster", cov_kwds={"groups": df[unit_col]})
att, se = did.params.get("tp", np.nan), did.bse.get("tp", np.nan)
pval = did.pvalues.get("tp", np.nan)

# ---------- Propensity Score Matching (1:1 NN) ----------
pre = df[df["post"]==0].copy()
to_avg = [y_col] + covs if covs else [y_col]
agg = pre.groupby(unit_col)[to_avg + [treat_col]].mean().reset_index()

X = agg[covs] if covs else agg[[y_col]]  # fallback if no covariates
X = X.fillna(X.median())
sc = StandardScaler(); Xs = sc.fit_transform(X)
from sklearn.linear_model import LogisticRegression
ps = LogisticRegression(max_iter=200).fit(Xs, agg[treat_col]).predict_proba(Xs)[:,1]
agg["ps"] = ps

treated_units = agg[agg[treat_col]==1]
control_units = agg[agg[treat_col]==0]
if len(treated_units)==0 or len(control_units)==0:
    att_psm = np.nan
else:
    nbrs = NearestNeighbors(n_neighbors=1).fit(control_units[["ps"]])
    dist, idx = nbrs.kneighbors(treated_units[["ps"]])
    matched_controls = control_units.iloc[idx.flatten()][unit_col].values
    pairs = list(zip(treated_units[unit_col].values, matched_controls))

    post = df[df["post"]==1]
    def unit_mean(u): 
        s = post.loc[post[unit_col]==u, y_col]
        return s.mean() if len(s) else np.nan
    diffs = []
    for tu, cu in pairs:
        diffs.append(unit_mean(tu) - unit_mean(cu))
    diffs = [d for d in diffs if not np.isnan(d)]
    att_psm = np.nanmean(diffs) if diffs else np.nan

# SMDs (pre-match)
def smd(a, b):
    return (np.nanmean(a)-np.nanmean(b))/np.sqrt(0.5*(np.nanvar(a)+np.nanvar(b)) + 1e-12)
rows=[]
for c in (covs if covs else [y_col]):
    tvals = agg.loc[agg[treat_col]==1, c].values
    cvals = agg.loc[agg[treat_col]==0, c].values
    rows.append((c, smd(tvals, cvals)))
import pandas as pd
smd_df = pd.DataFrame(rows, columns=["covariate","SMD"])
fig2 = plt.figure()
plt.barh(smd_df["covariate"], smd_df["SMD"])
plt.axvline(0.1, color="red", linestyle="--"); plt.axvline(-0.1, color="red", linestyle="--")
plt.title("Standardized Mean Differences (pre‑match)"); plt.tight_layout()
plt.savefig("figures/fig2_smd_prematch.png", dpi=150); plt.close()

# ---------- CausalImpact (optional) ----------
ci_summary = None
try:
    from causalimpact import CausalImpact  # tfcausalimpact
    # Aggregate to single treated series and a control (mean of controls)
    series = df.pivot_table(index=date_col, columns=unit_col, values=y_col)
    treated_cols = df.loc[df[treat_col]==1, unit_col].unique()
    control_cols = df.loc[df[treat_col]==0, unit_col].unique()
    if len(treated_cols)>0 and len(control_cols)>0:
        y_treated = series[treated_cols].mean(axis=1)
        X_controls = series[control_cols].mean(axis=1)
        ts = pd.concat([y_treated, X_controls], axis=1)
        ts.columns = ["y", "control"]
        pre_period  = [ts.index.min(), pd.to_datetime(t0) - pd.tseries.frequencies.to_offset(freq)]
        post_period = [pd.to_datetime(t0), ts.index.max()]
        impact = CausalImpact(ts, pre_period, post_period)
        impact.plot(figsize=(8,6))
        import matplotlib.pyplot as plt
        plt.tight_layout(); plt.savefig("figures/fig3_causalimpact.png", dpi=150); plt.close()
        ci_summary = str(impact.summary())
    else:
        ci_summary = "Skipped CausalImpact (need at least one treated and one control unit)"
except Exception as e:
    ci_summary = f"Skipped CausalImpact ({e})"

# ---------- write results ----------
res = {
    "did_att": float(att) if pd.notna(att) else None,
    "did_se": float(se) if pd.notna(se) else None,
    "did_p": float(pval) if pd.notna(pval) else None,
    "psm_att": float(att_psm) if not (att_psm is None or np.isnan(att_psm)) else None,
    "causalimpact": ci_summary
}
pathlib.Path("results").mkdir(exist_ok=True)
json.dump(res, open("results/results.json","w"), indent=2)
print(json.dumps(res, indent=2))
print("Figures -> figures/*.png | Results -> results/results.json")
