# %% [markdown]
# # Demand Forecasting & Inventory Planning for a Packaging Distributor
# **Goal:** forecast monthly demand for 15 packaging SKUs, choose the most accurate
# forecasting method for each SKU, and turn the forecast into an inventory plan
# (safety stock + reorder point) at a 95% service level.
#
# **Steps**
# 1. Load and explore 36 months of sales history
# 2. Build 5 forecasting methods
# 3. Pick the best method per SKU (validation) and measure accuracy honestly (test)
# 4. Forecast the next 6 months
# 5. Calculate safety stock and reorder points
# 6. Save charts and results
#
# Only uses pandas, numpy and matplotlib (all pre-installed in Google Colab).

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

os.makedirs("outputs", exist_ok=True)
df = pd.read_csv("data/packaging_sales_history.csv")
df["month"] = pd.to_datetime(df["month"])
print(df.head())
print(f"\n{df.sku.nunique()} SKUs, {df.month.nunique()} months: "
      f"{df.month.min():%b %Y} to {df.month.max():%b %Y}")

# %% [markdown]
# ## Step 1 - Explore the data
# Look for **trend** (growing over time?) and **seasonality** (repeating yearly pattern?).

# %%
total = df.groupby("month")["units_sold"].sum()
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(total.index, total.values, marker="o", color="#1f4e79")
ax.set_title("Total Monthly Units Sold - All 15 SKUs")
ax.set_ylabel("Units")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("outputs/01_total_sales_trend.png", dpi=150)
plt.show()

by_month = df.assign(m=df.month.dt.month).groupby("m")["units_sold"].sum()
print("Share of annual volume by calendar month (seasonality):")
print((by_month / by_month.sum()).round(3).to_string())

yearly = df.groupby(df.month.dt.year)["units_sold"].sum()
print("\nYear-over-year growth:", (yearly.pct_change() * 100).round(1).dropna().to_dict())

# %% [markdown]
# ## Step 2 - Five forecasting methods
# | Method | Idea |
# |---|---|
# | Naive | Next month = this month (the baseline every model must beat) |
# | 3-Month Moving Average | Average of the last 3 months |
# | Seasonal Naive | Next July = last July |
# | Simple Exponential Smoothing | Weighted average, recent months count more |
# | Holt-Winters | Smoothing that captures level + trend + seasonality |
#
# Each function takes the history (`y`) and returns forecasts for the next `h` months.

# %%
SEASON = 12

def naive(y, h):
    return np.repeat(y[-1], h)

def moving_average(y, h, window=3):
    return np.repeat(y[-window:].mean(), h)

def seasonal_naive(y, h):
    return np.array([y[len(y) - SEASON + (i % SEASON)] for i in range(h)])

def ses(y, h, alpha):
    level = y[0]
    for value in y[1:]:
        level = alpha * value + (1 - alpha) * level
    return np.repeat(level, h)

def holt_winters(y, h, alpha, beta, gamma):
    """Additive Holt-Winters. Needs at least 2 years of history."""
    level = y[:SEASON].mean()
    trend = (y[SEASON:2 * SEASON].mean() - y[:SEASON].mean()) / SEASON
    season = list(y[:SEASON] - level)
    for t in range(len(y)):
        s = season[t]
        last_level = level
        level = alpha * (y[t] - s) + (1 - alpha) * (level + trend)
        trend = beta * (level - last_level) + (1 - beta) * trend
        season.append(gamma * (y[t] - level) + (1 - gamma) * s)
    n = len(y)
    # season[n + i] holds the latest seasonal estimate for future month n + i
    return np.array([level + (i + 1) * trend + season[n + (i % SEASON)] for i in range(h)])

def one_step_error(y, model, params):
    """Average one-month-ahead error inside the history - used to tune parameters.
    Walks through the history once: predict month t, compare with actual, update."""
    errs = []
    if model is ses:
        (alpha,) = params
        level = y[0]
        for t in range(1, len(y)):
            errs.append(abs(y[t] - level))
            level = alpha * y[t] + (1 - alpha) * level
    else:
        alpha, beta, gamma = params
        level = y[:SEASON].mean()
        trend = (y[SEASON:2 * SEASON].mean() - y[:SEASON].mean()) / SEASON
        season = list(y[:SEASON] - level)
        for t in range(len(y)):
            if t >= SEASON:  # skip year 1 (used to set starting values)
                errs.append(abs(y[t] - (level + trend + season[t])))
            last_level = level
            level = alpha * (y[t] - season[t]) + (1 - alpha) * (level + trend)
            trend = beta * (level - last_level) + (1 - beta) * trend
            season.append(gamma * (y[t] - level) + (1 - gamma) * season[t])
    return np.mean(errs)

def tune(y, model):
    """Try a grid of smoothing parameters and keep the one with the lowest error."""
    if model is ses:
        grid = [(a,) for a in np.arange(0.1, 1.0, 0.1)]
    else:
        grid = [(a, b, g) for a in (0.1, 0.2, 0.3, 0.5)
                for b in (0.01, 0.05, 0.1) for g in (0.1, 0.3, 0.5)]
    return min(grid, key=lambda p: one_step_error(y, model, p))

def forecast(method, y, h):
    if method == "Naive":
        return naive(y, h)
    if method == "3-Month Moving Avg":
        return moving_average(y, h)
    if method == "Seasonal Naive":
        return seasonal_naive(y, h)
    if method == "Exp. Smoothing":
        return ses(y, h, *tune(y, ses))
    if method == "Holt-Winters":
        return holt_winters(y, h, *tune(y, holt_winters))

METHODS = ["Naive", "3-Month Moving Avg", "Seasonal Naive", "Exp. Smoothing", "Holt-Winters"]

# %% [markdown]
# ## Step 3 - Validation and test (honest accuracy)
# * **Validation:** train on months 1-24, forecast months 25-30 -> pick the best method per SKU.
# * **Test:** train on months 1-30, forecast months 31-36 (Jul-Dec 2025, includes the holiday peak)
#   using the method chosen in validation -> this is the accuracy we report.
#
# Picking the method on one period and scoring it on a *different* period stops us
# from "cheating" by choosing whatever happened to look best on the test data.
#
# **MAPE** = average of |actual - forecast| / actual. Lower is better.
# **WAPE** = total |error| / total actual units (portfolio-level accuracy, volume-weighted).

# %%
H = 6
skus = df.sku.unique()
series = {s: df[df.sku == s].sort_values("month")["units_sold"].to_numpy(float) for s in skus}
months = sorted(df.month.unique())

def mape(actual, fc):
    return np.mean(np.abs(actual - fc) / actual)

val_rows, test_rows = [], []
for s in skus:
    y = series[s]
    for m in METHODS:
        fc = forecast(m, y[:24], H)
        val_rows.append({"sku": s, "method": m, "val_mape": mape(y[24:30], fc)})
        fc_test = forecast(m, y[:30], H)
        for i in range(H):
            test_rows.append({"sku": s, "method": m, "month": months[30 + i],
                              "actual": y[30 + i], "forecast": round(fc_test[i])})

val = pd.DataFrame(val_rows)
test = pd.DataFrame(test_rows)
test["abs_error"] = (test.actual - test.forecast).abs()
test["ape"] = test.abs_error / test.actual

best = val.loc[val.groupby("sku")["val_mape"].idxmin(), ["sku", "method"]]
best = best.rename(columns={"method": "best_method"}).set_index("sku")["best_method"]
print("Best method per SKU (chosen on validation):")
print(best.value_counts().to_string())

# %%
summary = test.groupby("method").agg(MAPE=("ape", "mean"),
                                     abs_err=("abs_error", "sum"),
                                     actual=("actual", "sum"))
summary["WAPE"] = summary.abs_err / summary.actual
summary = summary[["MAPE", "WAPE"]].reindex(METHODS)

chosen = test[test.method == test.sku.map(best)]
summary.loc["Best-per-SKU (selected)"] = [chosen.ape.mean(),
                                          chosen.abs_error.sum() / chosen.actual.sum()]
print("Test accuracy, Jul-Dec 2025:")
print((summary * 100).round(1).astype(str).add("%").to_string())

naive_wape = summary.loc["Naive", "WAPE"]
best_wape = summary.loc["Best-per-SKU (selected)", "WAPE"]
improvement = (naive_wape - best_wape) / naive_wape
print(f"\nForecast error reduced by {improvement:.0%} vs. the naive baseline "
      f"(WAPE {naive_wape:.1%} -> {best_wape:.1%}); "
      f"forecast accuracy = {1 - best_wape:.1%}")

# %%
fig, ax = plt.subplots(figsize=(9, 4))
plot_df = summary["WAPE"] * 100
colors = ["#9dc3e6"] * (len(plot_df) - 1) + ["#1f4e79"]
ax.barh(plot_df.index, plot_df.values, color=colors)
for i, v in enumerate(plot_df.values):
    ax.text(v + 0.3, i, f"{v:.1f}%", va="center")
ax.invert_yaxis()
ax.set_xlim(0, plot_df.max() * 1.15)
ax.set_xlabel("Forecast error, WAPE % (lower is better)")
ax.set_title("Forecast Error by Method - Test Period Jul-Dec 2025")
plt.tight_layout()
plt.savefig("outputs/02_model_comparison.png", dpi=150)
plt.show()

tot = chosen.groupby("month")[["actual", "forecast"]].sum()
naive_tot = test[test.method == "Naive"].groupby("month")["forecast"].sum()
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(total.index, total.values, color="#7f7f7f", label="Actual units sold")
ax.plot(tot.index, tot.forecast, "o--", color="#1f4e79", label="Selected model forecast")
ax.plot(naive_tot.index, naive_tot.values, "x:", color="#c55a11", label="Naive baseline")
ax.set_title("Test Period: Forecast vs Actual (all SKUs)")
ax.set_ylabel("Units")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("outputs/03_forecast_vs_actual.png", dpi=150)
plt.show()

# %% [markdown]
# ## Step 4 - Forecast the next 6 months (Jan-Jun 2026)
# Re-train each SKU's chosen method on all 36 months.

# %%
future_months = pd.date_range(months[-1] + pd.offsets.MonthBegin(1), periods=H, freq="MS")
fc_rows = []
for s in skus:
    fc = forecast(best[s], series[s], H)
    for i, m in enumerate(future_months):
        fc_rows.append({"sku": s, "month": m, "forecast_units": max(0, round(fc[i]))})
future = pd.DataFrame(fc_rows)
print(future.pivot(index="sku", columns="month", values="forecast_units")
      .rename(columns=lambda c: c.strftime("%b %Y")).to_string())

# %% [markdown]
# ## Step 5 - Inventory plan: safety stock & reorder point
# * **Safety stock** = Z x (forecast error, measured as RMSE) x sqrt(lead time in months)
#   - Z = 1.645 for a 95% service level (stock out in only ~5% of cycles)
# * **Reorder point** = average monthly demand x lead time (months) + safety stock
#   - When on-hand + on-order inventory drops to this level, place a new order.

# %%
Z = 1.645
info = df.groupby("sku")[["description", "category", "unit_cost", "lead_time_weeks"]].first()
plan = info.copy()
plan["method"] = best
plan["avg_monthly_fc"] = future.groupby("sku")["forecast_units"].mean()
def rmse(frame):
    """Root mean squared forecast error per SKU - the typical size of a monthly miss."""
    e = frame.actual - frame.forecast
    return np.sqrt((e ** 2).groupby(frame.sku).mean())

plan["forecast_error_sd"] = rmse(chosen)
plan["lead_time_months"] = plan.lead_time_weeks / 4.33
plan["safety_stock"] = np.ceil(Z * plan.forecast_error_sd * np.sqrt(plan.lead_time_months))
plan["reorder_point"] = np.ceil(plan.avg_monthly_fc * plan.lead_time_months + plan.safety_stock)
plan["safety_stock_value"] = (plan.safety_stock * plan.unit_cost).round(2)
print(plan[["method", "avg_monthly_fc", "safety_stock", "reorder_point", "safety_stock_value"]]
      .round(0).to_string())
print(f"\nTotal safety stock investment: ${plan.safety_stock_value.sum():,.0f}")

# Better forecasts = smaller errors = less safety stock needed for the same 95% service level.
naive_test = test[test.method == "Naive"]
naive_sd = rmse(naive_test)
plan["safety_stock_if_naive"] = np.ceil(Z * naive_sd * np.sqrt(plan.lead_time_months))
naive_ss_value = (plan.safety_stock_if_naive * plan.unit_cost).sum()
ss_saving = naive_ss_value - plan.safety_stock_value.sum()
print(f"Safety stock needed with the naive forecast: ${naive_ss_value:,.0f}")
print(f"Savings from better forecasting: ${ss_saving:,.0f} "
      f"({ss_saving / naive_ss_value:.0%} less inventory at the same 95% service level)")

# %% [markdown]
# ## Step 6 - Save results
# CSV files feed the Excel dashboard (`build_excel.py`).

# %%
test.to_csv("outputs/backtest_results.csv", index=False)
val.to_csv("outputs/validation_results.csv", index=False)
future.to_csv("outputs/forecast_next_6_months.csv", index=False)
plan.reset_index().to_csv("outputs/inventory_plan.csv", index=False)
best.reset_index().to_csv("outputs/best_method_per_sku.csv", index=False)
summary.reset_index().rename(columns={"index": "method"}).to_csv(
    "outputs/model_summary.csv", index=False)
print("Saved all results to outputs/")
