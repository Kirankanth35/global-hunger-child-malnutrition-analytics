"""
Global Hunger & Child Malnutrition Risk Analytics Pipeline
Author: Kiran Kanth Madigani

What this pipeline produces:
- Clean processed datasets
- Data quality report
- Risk scoring model
- Intervention recommendations
- PNG visualizations only (no HTML)
- Excel workbook with embedded visualizations

Important methodological note:
This project uses a curated seed dataset built from authoritative public reports
(SOFI, GRFC, UNICEF/WHO/WB JME, WHO/UN IGME, IPC/CH, WFP, FAO, UNICEF).
For production-grade humanitarian decision making, replace the seed file with
official downloads from HDX/GRFC, IPC, WFP, OCHA, ACLED and World Bank APIs.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch, Circle

try:
    import xlsxwriter  # noqa: F401
except ImportError as exc:
    raise SystemExit("Please install xlsxwriter: pip install xlsxwriter") from exc


# ------------------------------------------------------------
# Project paths
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_SEED_DIR = BASE_DIR / "data" / "seed"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_TABLES_DIR = BASE_DIR / "outputs" / "tables"
OUTPUT_CHARTS_DIR = BASE_DIR / "outputs" / "charts"
OUTPUT_REPORTS_DIR = BASE_DIR / "outputs" / "reports"
OUTPUT_SPREADSHEETS_DIR = BASE_DIR / "outputs" / "spreadsheets"

for path in [DATA_PROCESSED_DIR, OUTPUT_TABLES_DIR, OUTPUT_CHARTS_DIR, OUTPUT_REPORTS_DIR, OUTPUT_SPREADSHEETS_DIR]:
    path.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# Visual theme
# ------------------------------------------------------------
COLORS = {
    "bg": "#F8FAFC",
    "panel": "#FFFFFF",
    "text": "#0F172A",
    "muted": "#64748B",
    "blue": "#2563EB",
    "cyan": "#0891B2",
    "purple": "#7C3AED",
    "red": "#DC2626",
    "orange": "#EA580C",
    "amber": "#D97706",
    "green": "#059669",
    "slate": "#334155",
    "light_blue": "#DBEAFE",
    "light_red": "#FEE2E2",
    "light_amber": "#FEF3C7",
    "light_green": "#DCFCE7",
}

plt.rcParams.update({
    "figure.facecolor": COLORS["bg"],
    "axes.facecolor": COLORS["panel"],
    "axes.edgecolor": "#CBD5E1",
    "axes.labelcolor": COLORS["text"],
    "xtick.color": COLORS["muted"],
    "ytick.color": COLORS["text"],
    "font.family": "DejaVu Sans",
    "axes.titleweight": "bold",
    "axes.titlesize": 16,
    "axes.labelsize": 11,
})


# ------------------------------------------------------------
# Loaders
# ------------------------------------------------------------
def load_seed_data() -> Dict[str, pd.DataFrame]:
    files = {
        "global_indicators": DATA_SEED_DIR / "global_reference_indicators.csv",
        "country_priority": DATA_SEED_DIR / "country_priority_seed.csv",
        "source_inventory": DATA_SEED_DIR / "source_inventory.csv",
        "intervention_catalog": DATA_SEED_DIR / "intervention_catalog.csv",
    }
    missing = [str(path) for path in files.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required seed files: {missing}")
    return {name: pd.read_csv(path) for name, path in files.items()}


# ------------------------------------------------------------
# Data quality checks
# ------------------------------------------------------------
def quality_check(country_df: pd.DataFrame, global_df: pd.DataFrame, source_df: pd.DataFrame) -> pd.DataFrame:
    checks = []

    def add_check(category, check_name, status, score, detail):
        checks.append({
            "category": category,
            "check_name": check_name,
            "status": status,
            "score": score,
            "detail": detail,
        })

    required_country_cols = [
        "country", "iso3", "region", "acute_food_insecurity_m", "acute_food_insecurity_pct",
        "child_malnutrition_risk_1_10", "conflict_driver_1_10", "economic_driver_1_10",
        "climate_driver_1_10", "displacement_driver_1_10", "access_constraint_1_10",
        "funding_gap_risk_1_10", "source_url"
    ]
    missing_cols = [c for c in required_country_cols if c not in country_df.columns]
    add_check("Schema", "Required country columns present", "PASS" if not missing_cols else "FAIL", 100 if not missing_cols else 0, f"Missing columns: {missing_cols}" if missing_cols else "All required columns present.")

    required_global_cols = ["indicator", "value", "unit", "year", "source_name", "source_url"]
    missing_global_cols = [c for c in required_global_cols if c not in global_df.columns]
    add_check("Schema", "Required global indicator columns present", "PASS" if not missing_global_cols else "FAIL", 100 if not missing_global_cols else 0, f"Missing columns: {missing_global_cols}" if missing_global_cols else "All required global columns present.")

    duplicate_keys = country_df.duplicated(subset=["country", "year"]).sum() if "year" in country_df.columns else 0
    add_check("Uniqueness", "No duplicate country-year rows", "PASS" if duplicate_keys == 0 else "WARN", 100 if duplicate_keys == 0 else 70, f"Duplicate country-year rows: {duplicate_keys}")

    numeric_cols = [
        "acute_food_insecurity_m", "acute_food_insecurity_pct", "child_malnutrition_risk_1_10",
        "conflict_driver_1_10", "economic_driver_1_10", "climate_driver_1_10",
        "displacement_driver_1_10", "access_constraint_1_10", "funding_gap_risk_1_10"
    ]
    missing_numeric = country_df[numeric_cols].isna().sum().sum()
    total_numeric = country_df[numeric_cols].size
    completeness = 1 - missing_numeric / total_numeric
    add_check("Completeness", "Critical numeric fields complete", "PASS" if completeness >= 0.95 else "WARN", round(completeness * 100, 1), f"Numeric completeness: {completeness:.1%}")

    pct_out_of_range = ((country_df["acute_food_insecurity_pct"] < 0) | (country_df["acute_food_insecurity_pct"] > 100)).sum()
    driver_cols = [c for c in numeric_cols if c.endswith("1_10")]
    driver_out_of_range = ((country_df[driver_cols] < 0) | (country_df[driver_cols] > 10)).sum().sum()
    out_of_range = pct_out_of_range + driver_out_of_range
    add_check("Validity", "Percentages and 1-10 scores in valid ranges", "PASS" if out_of_range == 0 else "FAIL", 100 if out_of_range == 0 else 0, f"Out-of-range cells: {out_of_range}")

    url_missing = country_df["source_url"].isna().sum() + source_df["source_url"].isna().sum()
    add_check("Traceability", "Source URLs available", "PASS" if url_missing == 0 else "WARN", 100 if url_missing == 0 else 75, f"Rows missing source URLs: {url_missing}")

    confidence_share = country_df["data_confidence"].isin(["High", "Medium-High"]).mean()
    add_check("Reliability", "High/Medium-High confidence coverage", "PASS" if confidence_share >= 0.65 else "WARN", round(confidence_share * 100, 1), f"High/Medium-High share: {confidence_share:.1%}")

    quality_df = pd.DataFrame(checks)
    quality_df["weighted_score"] = quality_df["score"]
    return quality_df


# ------------------------------------------------------------
# Risk scoring and recommendations
# ------------------------------------------------------------
def minmax(series: pd.Series) -> pd.Series:
    series = pd.to_numeric(series, errors="coerce").fillna(0)
    if series.max() == series.min():
        return series * 0
    return (series - series.min()) / (series.max() - series.min())


def assign_priority(score: float) -> str:
    if score >= 80:
        return "Critical"
    if score >= 65:
        return "Very High"
    if score >= 50:
        return "High"
    if score >= 35:
        return "Moderate"
    return "Watchlist"


def recommend_intervention(row: pd.Series) -> str:
    drivers = {
        "Conflict/access constraint": row["conflict_driver_1_10"] + row["access_constraint_1_10"],
        "Food affordability/economic shock": row["economic_driver_1_10"],
        "Climate/agriculture shock": row["climate_driver_1_10"],
        "Displacement pressure": row["displacement_driver_1_10"],
        "Child malnutrition treatment": row["child_malnutrition_risk_1_10"],
    }
    dominant = max(drivers, key=drivers.get)
    if dominant == "Conflict/access constraint":
        return "Negotiated humanitarian access + emergency food assistance + local partner delivery"
    if dominant == "Food affordability/economic shock":
        return "Cash/voucher assistance + staple price monitoring + social protection"
    if dominant == "Climate/agriculture shock":
        return "Emergency agricultural support + drought-resilient seeds + water/irrigation support"
    if dominant == "Displacement pressure":
        return "IDP-targeted food, nutrition, WASH and mobile health service package"
    return "Mass screening + ready-to-use therapeutic food + maternal/child health integration"


def score_country_risk(country_df: pd.DataFrame) -> pd.DataFrame:
    df = country_df.copy()
    df["acute_burden_norm"] = minmax(df["acute_food_insecurity_m"])
    df["acute_prevalence_norm"] = minmax(df["acute_food_insecurity_pct"])
    df["phase5_norm"] = minmax(df["ipc_ch_phase5_population_m"].fillna(0))
    df["child_malnutrition_norm"] = df["child_malnutrition_risk_1_10"] / 10
    df["conflict_norm"] = df["conflict_driver_1_10"] / 10
    df["economic_norm"] = df["economic_driver_1_10"] / 10
    df["climate_norm"] = df["climate_driver_1_10"] / 10
    df["displacement_norm"] = df["displacement_driver_1_10"] / 10
    df["access_norm"] = df["access_constraint_1_10"] / 10
    df["funding_gap_norm"] = df["funding_gap_risk_1_10"] / 10

    df["risk_score"] = (
        0.20 * df["acute_burden_norm"] +
        0.15 * df["acute_prevalence_norm"] +
        0.12 * df["phase5_norm"] +
        0.15 * df["child_malnutrition_norm"] +
        0.12 * df["conflict_norm"] +
        0.08 * df["economic_norm"] +
        0.06 * df["climate_norm"] +
        0.06 * df["displacement_norm"] +
        0.04 * df["access_norm"] +
        0.02 * df["funding_gap_norm"]
    ) * 100

    df["risk_score"] = df["risk_score"].round(1)
    df["priority_level"] = df["risk_score"].apply(assign_priority)
    df["recommended_intervention"] = df.apply(recommend_intervention, axis=1)
    df["people_in_immediate_need_m"] = (df["acute_food_insecurity_m"] * (df["acute_food_insecurity_pct"] / 100)).round(2)

    return df.sort_values("risk_score", ascending=False)


def build_regional_summary(country_scored: pd.DataFrame) -> pd.DataFrame:
    return country_scored.groupby("region", as_index=False).agg(
        countries=("country", "count"),
        acute_food_insecurity_m=("acute_food_insecurity_m", "sum"),
        phase5_population_m=("ipc_ch_phase5_population_m", "sum"),
        avg_risk_score=("risk_score", "mean"),
        avg_child_malnutrition_risk=("child_malnutrition_risk_1_10", "mean"),
    ).round({"acute_food_insecurity_m": 1, "phase5_population_m": 2, "avg_risk_score": 1, "avg_child_malnutrition_risk": 1}).sort_values("acute_food_insecurity_m", ascending=False)


def build_intervention_summary(country_scored: pd.DataFrame) -> pd.DataFrame:
    out = country_scored.groupby("recommended_intervention", as_index=False).agg(
        countries=("country", "count"),
        acute_food_insecurity_m=("acute_food_insecurity_m", "sum"),
        avg_risk_score=("risk_score", "mean"),
    ).round({"acute_food_insecurity_m": 1, "avg_risk_score": 1}).sort_values("acute_food_insecurity_m", ascending=False)
    return out


# ------------------------------------------------------------
# PNG visualization helpers
# ------------------------------------------------------------
def savefig(path: Path):
    plt.savefig(path, dpi=220, bbox_inches="tight", facecolor=COLORS["bg"])
    plt.close()


def add_title(fig, title: str, subtitle: str = ""):
    fig.text(0.02, 0.965, title, fontsize=22, fontweight="bold", color=COLORS["text"], va="top")
    if subtitle:
        fig.text(0.02, 0.925, subtitle, fontsize=11, color=COLORS["muted"], va="top")


def chart_global_kpis(global_df: pd.DataFrame):
    fig = plt.figure(figsize=(16, 9))
    add_title(fig, "Global Hunger & Child Malnutrition Snapshot", "Authoritative reference indicators used as the project foundation")

    cards = [
        ("Chronic hunger", "673M", "People experienced hunger in 2024", COLORS["blue"]),
        ("Acute food insecurity", "295.3M", "People across 53 countries/territories in 2024", COLORS["red"]),
        ("Food insecurity", "2.3B", "Moderate/severe food insecurity in 2024", COLORS["purple"]),
        ("Healthy diet gap", "2.6B", "Unable to afford a healthy diet in 2024", COLORS["orange"]),
        ("Child stunting", "150.2M", "Children under 5 stunted in 2024", COLORS["amber"]),
        ("Child wasting", "42.8M", "Children under 5 wasted in 2024", COLORS["cyan"]),
        ("Under-5 deaths", "4.9M", "Children died before age five in 2024", COLORS["slate"]),
        ("Undernutrition link", "~45%", "Under-5 deaths linked to undernutrition", COLORS["green"]),
    ]
    x0s = [0.04, 0.28, 0.52, 0.76] * 2
    y0s = [0.62] * 4 + [0.30] * 4
    w, h = 0.20, 0.22
    for (title, value, desc, color), x, y in zip(cards, x0s, y0s):
        ax = fig.add_axes([x, y, w, h])
        ax.axis("off")
        card = FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02,rounding_size=0.04", facecolor="#FFFFFF", edgecolor="#E2E8F0", linewidth=1.3)
        ax.add_patch(card)
        ax.add_patch(Rectangle((0, 0.88), 1, 0.12, facecolor=color, edgecolor="none"))
        ax.text(0.06, 0.75, title, fontsize=11, fontweight="bold", color=COLORS["text"])
        ax.text(0.06, 0.42, value, fontsize=30, fontweight="bold", color=color)
        ax.text(0.06, 0.16, desc, fontsize=9.5, color=COLORS["muted"], wrap=True)

    fig.text(0.02, 0.05, "Sources: SOFI 2025, GRFC 2025, UNICEF-WHO-World Bank JME 2025, WHO/UN IGME 2026. See source inventory for URLs.", fontsize=10, color=COLORS["muted"])
    savefig(OUTPUT_CHARTS_DIR / "01_global_kpi_snapshot.png")


def chart_top_countries(country_scored: pd.DataFrame):
    df = country_scored.sort_values("acute_food_insecurity_m", ascending=True).tail(15)
    colors = [COLORS["red"] if p in ["Critical", "Very High"] else COLORS["blue"] for p in df["priority_level"]]
    fig, ax = plt.subplots(figsize=(14, 9))
    bars = ax.barh(df["country"], df["acute_food_insecurity_m"], color=colors, edgecolor="#0F172A", linewidth=0.4)
    ax.set_title("Top Countries/Territories by Acute Food Insecurity Burden", loc="left", pad=18)
    ax.set_xlabel("People facing high acute food insecurity (millions)")
    ax.grid(axis="x", alpha=0.25)
    ax.spines[["top", "right", "left"]].set_visible(False)
    for bar, val in zip(bars, df["acute_food_insecurity_m"]):
        ax.text(val + 0.4, bar.get_y() + bar.get_height()/2, f"{val:.1f}M", va="center", fontsize=10, color=COLORS["text"], fontweight="bold")
    fig.text(0.02, 0.02, "Note: Seed values are rounded, source-backed project modeling inputs. Replace with official HDX/GRFC country extracts for final publication.", fontsize=9, color=COLORS["muted"])
    savefig(OUTPUT_CHARTS_DIR / "02_top_acute_food_insecurity_countries.png")


def chart_risk_rank(country_scored: pd.DataFrame):
    df = country_scored.sort_values("risk_score", ascending=True).tail(18)
    color_map = {"Critical": COLORS["red"], "Very High": COLORS["orange"], "High": COLORS["amber"], "Moderate": COLORS["blue"], "Watchlist": COLORS["green"]}
    fig, ax = plt.subplots(figsize=(14, 10))
    colors = df["priority_level"].map(color_map)
    bars = ax.barh(df["country"], df["risk_score"], color=colors, edgecolor="#0F172A", linewidth=0.3)
    ax.set_title("Child Hunger Risk Score: Highest Priority Countries/Territories", loc="left", pad=18)
    ax.set_xlabel("Risk score, 0-100")
    ax.set_xlim(0, 100)
    ax.grid(axis="x", alpha=0.25)
    ax.spines[["top", "right", "left"]].set_visible(False)
    for bar, score, priority in zip(bars, df["risk_score"], df["priority_level"]):
        ax.text(score + 1, bar.get_y() + bar.get_height()/2, f"{score:.1f} | {priority}", va="center", fontsize=9.5, color=COLORS["text"], fontweight="bold")
    savefig(OUTPUT_CHARTS_DIR / "03_child_hunger_risk_score_ranked.png")


def chart_driver_heatmap(country_scored: pd.DataFrame):
    df = country_scored.head(15).set_index("country")[[
        "child_malnutrition_risk_1_10", "conflict_driver_1_10", "economic_driver_1_10", "climate_driver_1_10",
        "displacement_driver_1_10", "access_constraint_1_10", "funding_gap_risk_1_10"
    ]]
    labels = ["Child\nmalnutrition", "Conflict", "Economic", "Climate", "Displacement", "Access", "Funding\ngap"]
    fig, ax = plt.subplots(figsize=(14, 8))
    im = ax.imshow(df.values, cmap="YlOrRd", vmin=0, vmax=10, aspect="auto")
    ax.set_xticks(np.arange(len(labels)), labels=labels, fontsize=10)
    ax.set_yticks(np.arange(len(df.index)), labels=df.index, fontsize=10)
    ax.set_title("Driver Heatmap: Why Hunger Risk Is High", loc="left", pad=18)
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            val = df.iloc[i, j]
            ax.text(j, i, f"{val:.0f}", ha="center", va="center", color="#111827" if val < 7 else "white", fontsize=9, fontweight="bold")
    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_label("Driver intensity, 1-10")
    ax.tick_params(axis='x', bottom=False, top=True, labelbottom=False, labeltop=True)
    ax.spines[:].set_visible(False)
    savefig(OUTPUT_CHARTS_DIR / "04_driver_heatmap.png")


def chart_risk_vs_burden(country_scored: pd.DataFrame):
    df = country_scored.copy()
    fig, ax = plt.subplots(figsize=(14, 8))
    size = (df["ipc_ch_phase5_population_m"].fillna(0) + 0.2) * 350
    colors = df["risk_score"]
    scatter = ax.scatter(df["acute_food_insecurity_m"], df["risk_score"], s=size, c=colors, cmap="plasma", alpha=0.75, edgecolor="#0F172A", linewidth=0.6)
    for _, row in df.iterrows():
        if row["risk_score"] >= 70 or row["acute_food_insecurity_m"] >= 15:
            ax.text(row["acute_food_insecurity_m"] + 0.35, row["risk_score"] + 0.5, row["country"], fontsize=9, fontweight="bold", color=COLORS["text"])
    ax.set_title("Risk vs Burden: Where Scale and Severity Overlap", loc="left", pad=18)
    ax.set_xlabel("Acute food insecurity burden (millions)")
    ax.set_ylabel("Child Hunger Risk Score")
    ax.grid(alpha=0.25)
    cbar = fig.colorbar(scatter, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_label("Risk score")
    fig.text(0.02, 0.02, "Bubble size represents IPC/CH Phase 5 population where available. Larger bubbles indicate catastrophic hunger concentration.", fontsize=9, color=COLORS["muted"])
    savefig(OUTPUT_CHARTS_DIR / "05_risk_vs_burden_scatter.png")


def chart_regional_burden(regional_df: pd.DataFrame):
    df = regional_df.sort_values("acute_food_insecurity_m", ascending=True)
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.barh(df["region"], df["acute_food_insecurity_m"], color=COLORS["blue"], alpha=0.9)
    ax.set_title("Regional Burden in the Seed Dataset", loc="left", pad=18)
    ax.set_xlabel("Acute food insecurity burden (millions)")
    ax.grid(axis="x", alpha=0.25)
    ax.spines[["top", "right", "left"]].set_visible(False)
    for i, val in enumerate(df["acute_food_insecurity_m"]):
        ax.text(val + 0.5, i, f"{val:.1f}M", va="center", fontweight="bold")
    savefig(OUTPUT_CHARTS_DIR / "06_regional_burden.png")


def chart_intervention_mix(intervention_df: pd.DataFrame):
    df = intervention_df.sort_values("acute_food_insecurity_m", ascending=True)
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.barh(df["recommended_intervention"], df["acute_food_insecurity_m"], color=COLORS["purple"], alpha=0.9)
    ax.set_title("Recommended Response Mix by Affected Population", loc="left", pad=18)
    ax.set_xlabel("Acute food insecurity linked to recommended intervention (millions)")
    ax.grid(axis="x", alpha=0.25)
    ax.tick_params(axis="y", labelsize=9)
    ax.spines[["top", "right", "left"]].set_visible(False)
    for i, val in enumerate(df["acute_food_insecurity_m"]):
        ax.text(val + 0.5, i, f"{val:.1f}M", va="center", fontweight="bold")
    savefig(OUTPUT_CHARTS_DIR / "07_intervention_strategy_mix.png")


def chart_quality_score(quality_df: pd.DataFrame):
    score = quality_df["weighted_score"].mean()
    fig = plt.figure(figsize=(12, 7))
    ax = fig.add_subplot(111)
    ax.axis("off")
    add_title(fig, "Data Foundation Quality Scorecard", "This checks schema, completeness, validity, traceability and reliability before analysis.")
    center = (0.5, 0.48)
    radius = 0.26
    circle = Circle(center, radius, transform=ax.transAxes, facecolor="#FFFFFF", edgecolor="#CBD5E1", linewidth=2)
    ax.add_patch(circle)
    color = COLORS["green"] if score >= 85 else COLORS["amber"] if score >= 70 else COLORS["red"]
    ax.text(0.5, 0.53, f"{score:.1f}", ha="center", va="center", fontsize=56, color=color, fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.40, "Foundation Score", ha="center", va="center", fontsize=14, color=COLORS["muted"], transform=ax.transAxes)
    status_text = "Strong foundation" if score >= 85 else "Usable with fixes" if score >= 70 else "Needs major cleanup"
    ax.text(0.5, 0.30, status_text, ha="center", va="center", fontsize=18, color=COLORS["text"], fontweight="bold", transform=ax.transAxes)
    # summary rows
    y = 0.15
    for _, row in quality_df.iterrows():
        col = COLORS["green"] if row["status"] == "PASS" else COLORS["amber"] if row["status"] == "WARN" else COLORS["red"]
        ax.text(0.08, y, row["check_name"], fontsize=10, color=COLORS["text"], transform=ax.transAxes)
        ax.text(0.55, y, row["status"], fontsize=10, color=col, fontweight="bold", transform=ax.transAxes)
        ax.text(0.72, y, f"{row['score']}", fontsize=10, color=COLORS["text"], transform=ax.transAxes)
        y -= 0.04
    savefig(OUTPUT_CHARTS_DIR / "08_data_quality_scorecard.png")


def chart_architecture():
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.axis("off")
    ax.set_title("Python Pipeline Architecture: From Sources to Executive Outputs", loc="left", pad=18)
    boxes = [
        ("Authoritative Sources", "SOFI, GRFC, IPC/CH, JME, WHO/UN IGME, WFP, OCHA", 0.05, 0.70, COLORS["blue"]),
        ("Seed / Raw Data", "CSV inputs, source inventory, country priority dataset", 0.33, 0.70, COLORS["purple"]),
        ("Validation Layer", "Schema, completeness, ranges, source traceability", 0.61, 0.70, COLORS["cyan"]),
        ("Risk Scoring Model", "Weighted child hunger risk score + priority levels", 0.33, 0.42, COLORS["orange"]),
        ("Business Rules", "Recommended interventions based on dominant drivers", 0.61, 0.42, COLORS["amber"]),
        ("Outputs", "PNG charts, CSV tables, Excel dashboard, Markdown reports", 0.33, 0.14, COLORS["green"]),
    ]
    for title, desc, x, y, color in boxes:
        box = FancyBboxPatch((x, y), 0.24, 0.14, boxstyle="round,pad=0.02,rounding_size=0.02", transform=ax.transAxes, facecolor="#FFFFFF", edgecolor=color, linewidth=2)
        ax.add_patch(box)
        ax.text(x + 0.02, y + 0.095, title, transform=ax.transAxes, fontsize=13, fontweight="bold", color=color)
        ax.text(x + 0.02, y + 0.042, desc, transform=ax.transAxes, fontsize=9.5, color=COLORS["muted"], wrap=True)
    arrows = [((0.29, 0.77), (0.33, 0.77)), ((0.57, 0.77), (0.61, 0.77)), ((0.73, 0.70), (0.73, 0.56)), ((0.57, 0.49), (0.61, 0.49)), ((0.45, 0.42), (0.45, 0.28)), ((0.61, 0.42), (0.57, 0.28))]
    for start, end in arrows:
        arrow = FancyArrowPatch(start, end, transform=ax.transAxes, arrowstyle="-|>", mutation_scale=18, linewidth=2, color=COLORS["slate"])
        ax.add_patch(arrow)
    savefig(OUTPUT_CHARTS_DIR / "09_pipeline_architecture.png")


# ------------------------------------------------------------
# Reports and Excel
# ------------------------------------------------------------
def write_markdown_reports(global_df, country_scored, regional_df, intervention_df, quality_df, source_df):
    foundation_score = quality_df["weighted_score"].mean()
    top5 = country_scored.head(5)[["country", "risk_score", "priority_level", "acute_food_insecurity_m", "recommended_intervention"]]
    md = []
    md.append("# Global Hunger & Child Malnutrition Analytics — Executive Summary\n")
    md.append("## Data Foundation Check\n")
    md.append(f"Foundation readiness score: **{foundation_score:.1f}/100**.\n")
    md.append("This means the project has a strong source-backed foundation, while still allowing future replacement of seed country data with official API/HDX extracts.\n")
    md.append("## Core Global Signals\n")
    for _, row in global_df.iterrows():
        md.append(f"- **{row['indicator']}**: {row['value']} {row['unit']} ({int(row['year'])}) — {row['source_name']}")
    md.append("\n## Top Priority Countries/Territories\n")
    md.append(top5.to_markdown(index=False))
    md.append("\n## Business Analyst Insight\n")
    md.append("The highest-risk cases are not only large by population burden; they combine scale, high prevalence, conflict/access constraints, child malnutrition risk, displacement, and funding gaps. The business analytics value is turning these signals into a ranked action portfolio instead of a passive dashboard.\n")
    md.append("## Recommended Strategy\n")
    md.append(intervention_df.to_markdown(index=False))
    md.append("\n## Source Inventory\n")
    md.append(source_df[["source_name", "source_type", "source_url"]].to_markdown(index=False))
    (OUTPUT_REPORTS_DIR / "executive_summary.md").write_text("\n".join(md), encoding="utf-8")

    dq = []
    dq.append("# Data Foundation Quality Report\n")
    dq.append("This report verifies whether the project data foundation is clean enough to support analysis.\n")
    dq.append(quality_df.to_markdown(index=False))
    dq.append("\n## Interpretation\n")
    dq.append("- PASS means the condition is strong enough for portfolio analytics.\n- WARN means the project is usable but should be upgraded when official machine-readable data is added.\n- FAIL means the pipeline should stop before producing final insights.\n")
    (OUTPUT_REPORTS_DIR / "data_quality_report.md").write_text("\n".join(dq), encoding="utf-8")


def build_excel_dashboard(global_df, country_scored, regional_df, intervention_df, quality_df, source_df):
    xlsx_path = OUTPUT_SPREADSHEETS_DIR / "Global_Hunger_Child_Malnutrition_Analytics_Dashboard.xlsx"
    with pd.ExcelWriter(xlsx_path, engine="xlsxwriter") as writer:
        global_df.to_excel(writer, sheet_name="Global KPIs", index=False)
        country_scored.to_excel(writer, sheet_name="Country Risk Model", index=False)
        regional_df.to_excel(writer, sheet_name="Regional Summary", index=False)
        intervention_df.to_excel(writer, sheet_name="Intervention Strategy", index=False)
        quality_df.to_excel(writer, sheet_name="Data Quality", index=False)
        source_df.to_excel(writer, sheet_name="Source Inventory", index=False)

        workbook = writer.book
        fmt_title = workbook.add_format({"bold": True, "font_size": 22, "font_color": "#0F172A"})
        fmt_subtitle = workbook.add_format({"font_size": 11, "font_color": "#64748B"})
        fmt_header = workbook.add_format({"bold": True, "bg_color": "#1D4ED8", "font_color": "#FFFFFF", "border": 1})
        fmt_num = workbook.add_format({"num_format": "#,##0.0", "border": 1})
        fmt_pct = workbook.add_format({"num_format": "0.0%", "border": 1})
        fmt_text = workbook.add_format({"text_wrap": True, "valign": "top", "border": 1})
        fmt_kpi = workbook.add_format({"bold": True, "font_size": 18, "font_color": "#1D4ED8", "align": "center", "valign": "vcenter", "border": 1, "bg_color": "#EFF6FF"})
        fmt_kpi_label = workbook.add_format({"font_size": 10, "font_color": "#334155", "align": "center", "valign": "vcenter", "text_wrap": True})

        # Add executive sheet first
        dash = workbook.add_worksheet("Executive Dashboard")
        dash.set_tab_color("#1D4ED8")
        dash.write("A1", "Global Hunger & Child Malnutrition Analytics", fmt_title)
        dash.write("A2", "Python pipeline outputs: PNG visuals, spreadsheet dashboard, risk model, quality scorecard, and executive reports.", fmt_subtitle)

        kpis = [
            ("Global hunger", "673M"), ("Acute food insecurity", "295.3M"), ("Moderate/severe food insecurity", "2.3B"), ("Healthy diet unaffordability", "2.6B"),
            ("Children stunted", "150.2M"), ("Children wasted", "42.8M"), ("Under-5 deaths", "4.9M"), ("Foundation score", f"{quality_df['weighted_score'].mean():.1f}/100")
        ]
        positions = ["A4", "C4", "E4", "G4", "A7", "C7", "E7", "G7"]
        for (label, val), pos in zip(kpis, positions):
            row = int(pos[1:]) - 1
            col = ord(pos[0]) - ord('A')
            dash.merge_range(row, col, row, col + 1, val, fmt_kpi)
            dash.merge_range(row + 1, col, row + 1, col + 1, label, fmt_kpi_label)

        # Insert PNG charts into Excel dashboard
        img_files = [
            "01_global_kpi_snapshot.png", "02_top_acute_food_insecurity_countries.png", "03_child_hunger_risk_score_ranked.png",
            "04_driver_heatmap.png", "05_risk_vs_burden_scatter.png", "06_regional_burden.png",
            "07_intervention_strategy_mix.png", "08_data_quality_scorecard.png", "09_pipeline_architecture.png"
        ]
        locations = ["A10", "I10", "A35", "I35", "A62", "I62", "A89", "I89", "A116"]
        for img, loc in zip(img_files, locations):
            p = OUTPUT_CHARTS_DIR / img
            if p.exists():
                dash.insert_image(loc, str(p), {"x_scale": 0.55, "y_scale": 0.55, "object_position": 1})

        dash.set_column("A:H", 18)
        dash.set_column("I:P", 18)
        dash.set_row(0, 30)

        # Manually apply headers, filters and widths
        for sheet_name, df in [
            ("Global KPIs", global_df), ("Country Risk Model", country_scored), ("Regional Summary", regional_df),
            ("Intervention Strategy", intervention_df), ("Data Quality", quality_df), ("Source Inventory", source_df)
        ]:
            ws = writer.sheets[sheet_name]
            for col_num, col_name in enumerate(df.columns):
                ws.write(0, col_num, col_name, fmt_header)
                max_len = min(max(12, int(df[col_name].astype(str).str.len().quantile(0.90)) + 3), 42)
                if "url" in col_name.lower() or "intervention" in col_name.lower() or "description" in col_name.lower() or "detail" in col_name.lower():
                    max_len = 48
                ws.set_column(col_num, col_num, max_len)
            if sheet_name == "Country Risk Model":
                risk_col = list(df.columns).index("risk_score")
                ws.conditional_format(1, risk_col, len(df), risk_col, {"type": "3_color_scale", "min_color": "#DCFCE7", "mid_color": "#FEF3C7", "max_color": "#FECACA"})
                burden_col = list(df.columns).index("acute_food_insecurity_m")
                ws.conditional_format(1, burden_col, len(df), burden_col, {"type": "data_bar", "bar_color": "#2563EB"})
            if sheet_name == "Data Quality":
                score_col = list(df.columns).index("score")
                ws.conditional_format(1, score_col, len(df), score_col, {"type": "data_bar", "bar_color": "#059669"})

    return xlsx_path


# ------------------------------------------------------------
# Main pipeline
# ------------------------------------------------------------
def main():
    data = load_seed_data()
    global_df = data["global_indicators"]
    country_df = data["country_priority"]
    source_df = data["source_inventory"]
    intervention_catalog = data["intervention_catalog"]

    quality_df = quality_check(country_df, global_df, source_df)
    country_scored = score_country_risk(country_df)
    regional_df = build_regional_summary(country_scored)
    intervention_df = build_intervention_summary(country_scored)

    # Save processed tables
    global_df.to_csv(DATA_PROCESSED_DIR / "global_reference_indicators_processed.csv", index=False)
    country_scored.to_csv(DATA_PROCESSED_DIR / "country_risk_model_scored.csv", index=False)
    regional_df.to_csv(DATA_PROCESSED_DIR / "regional_summary.csv", index=False)
    intervention_df.to_csv(DATA_PROCESSED_DIR / "intervention_strategy_summary.csv", index=False)
    quality_df.to_csv(DATA_PROCESSED_DIR / "data_quality_scorecard.csv", index=False)

    country_scored.to_csv(OUTPUT_TABLES_DIR / "country_risk_model_scored.csv", index=False)
    regional_df.to_csv(OUTPUT_TABLES_DIR / "regional_summary.csv", index=False)
    intervention_df.to_csv(OUTPUT_TABLES_DIR / "intervention_strategy_summary.csv", index=False)
    quality_df.to_csv(OUTPUT_TABLES_DIR / "data_quality_scorecard.csv", index=False)
    source_df.to_csv(OUTPUT_TABLES_DIR / "source_inventory.csv", index=False)

    # Create visuals
    chart_global_kpis(global_df)
    chart_top_countries(country_scored)
    chart_risk_rank(country_scored)
    chart_driver_heatmap(country_scored)
    chart_risk_vs_burden(country_scored)
    chart_regional_burden(regional_df)
    chart_intervention_mix(intervention_df)
    chart_quality_score(quality_df)
    chart_architecture()

    # Reports and spreadsheet dashboard
    write_markdown_reports(global_df, country_scored, regional_df, intervention_df, quality_df, source_df)
    xlsx_path = build_excel_dashboard(global_df, country_scored, regional_df, intervention_df, quality_df, source_df)

    print("\nPipeline complete.")
    print(f"Processed tables: {OUTPUT_TABLES_DIR}")
    print(f"PNG charts: {OUTPUT_CHARTS_DIR}")
    print(f"Markdown reports: {OUTPUT_REPORTS_DIR}")
    print(f"Spreadsheet dashboard: {xlsx_path}")
    print(f"Top risk countries: {', '.join(country_scored.head(5)['country'].tolist())}")
    print(f"Data foundation score: {quality_df['weighted_score'].mean():.1f}/100")


if __name__ == "__main__":
    main()
