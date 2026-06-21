# Global Hunger & Child Malnutrition Risk Analytics

A recruiter-ready **Business Analyst / Data Analyst portfolio project** focused on global hunger, acute food insecurity, child malnutrition, and humanitarian response prioritization.

This project does **not** create a single HTML dashboard. Every output is generated through Python as:

- PNG charts
- CSV processed tables
- Excel spreadsheet dashboard with embedded visuals
- Markdown reports
- Clean Python pipeline

## Why this project matters

Hunger is not only a food supply problem. It is often created by a combination of conflict, access restrictions, food price shocks, climate events, displacement, weak health systems, and funding gaps. This project converts those complex signals into a clean business analytics workflow that a recruiter can understand.

## Project question

**Where are children and families at the highest risk of severe hunger, what is driving the crisis, and which interventions should be prioritized first?**

## Core metrics used

| Metric | Latest source-backed value | Source |
|---|---:|---|
| People experiencing chronic hunger | 673M in 2024 | SOFI 2025 |
| People facing acute food insecurity in food-crisis contexts | 295.3M in 2024 | GRFC 2025 |
| Countries/territories covered in GRFC acute crisis analysis | 53 | GRFC 2025 |
| Moderate/severe food insecurity | 2.3B in 2024 | SOFI 2025 |
| Unable to afford a healthy diet | 2.6B in 2024 | SOFI 2025 |
| Children under 5 stunted | 150.2M in 2024 | UNICEF-WHO-World Bank JME |
| Children under 5 wasted | 42.8M in 2024 | UNICEF-WHO-World Bank JME |
| Under-5 deaths | 4.9M in 2024 | WHO/UN IGME |

## What the pipeline creates

```text
global_hunger_child_malnutrition_python_project/
├── data/
│   ├── seed/
│   │   ├── global_reference_indicators.csv
│   │   ├── country_priority_seed.csv
│   │   ├── source_inventory.csv
│   │   └── intervention_catalog.csv
│   └── processed/
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.csv
│   └── methodology.md
├── outputs/
│   ├── charts/                  # PNG-only visual outputs
│   ├── tables/                  # CSV analysis outputs
│   ├── spreadsheets/            # Excel workbook dashboard
│   └── reports/                 # Markdown reports
├── src/
│   └── pipeline.py
├── requirements.txt
└── README.md
```

## Main outputs

After running the pipeline, these are created:

### PNG charts

1. <img width="3352" height="1863" alt="01_global_kpi_snapshot" src="https://github.com/user-attachments/assets/a8d7f81b-ca6b-4341-96a5-582bad7da0f2" />

2. <img width="3012" height="1845" alt="02_top_acute_food_insecurity_countries" src="https://github.com/user-attachments/assets/49851ad4-ae07-4a57-a94e-475780b90944" />

3. <img width="3017" height="1928" alt="03_child_hunger_risk_score_ranked" src="https://github.com/user-attachments/assets/37a6bc89-d2c4-4a23-a4b6-cefcfa96b9fd" />

4. <img width="3094" height="1587" alt="04_driver_heatmap" src="https://github.com/user-attachments/assets/d73ae43b-11c3-456f-b81e-cc33495cd2ae" />

5. <img width="2903" height="1656" alt="05_risk_vs_burden_scatter" src="https://github.com/user-attachments/assets/0ad9f0d7-5591-4a77-b847-1a7d373260b4" />

6. <img width="2735" height="1420" alt="06_regional_burden" src="https://github.com/user-attachments/assets/a3e3b2aa-ac94-4a80-9700-0841c582cf59" />

7. <img width="3700" height="1589" alt="07_intervention_strategy_mix" src="https://github.com/user-attachments/assets/edf72314-934f-4d80-969a-0c8b28817aea" />

8. <img width="2367" height="1474" alt="08_data_quality_scorecard" src="https://github.com/user-attachments/assets/ba40ec62-b011-4c55-8e49-e681f3045ffb" />

9. <img width="2771" height="1660" alt="09_pipeline_architecture" src="https://github.com/user-attachments/assets/a76f1e15-10ae-4e67-ae3a-05f51773db1d" />


### Spreadsheet dashboard

`outputs/spreadsheets/Global_Hunger_Child_Malnutrition_Analytics_Dashboard.xlsx`

Includes:
- Executive dashboard sheet with embedded PNG visuals
- Global KPI table
- Country risk model
- Regional summary
- Intervention strategy
- Data quality checks
- Source inventory

### Reports

- `outputs/reports/executive_summary.md`
- `outputs/reports/data_quality_report.md`

## Risk scoring model

The risk model uses a weighted score from 0 to 100.

```text
Risk Score =
20% acute food insecurity burden
15% acute food insecurity prevalence
12% IPC/CH Phase 5 population
15% child malnutrition risk
12% conflict intensity
8% economic/food affordability stress
6% climate shock
6% displacement pressure
4% humanitarian access constraint
2% funding gap risk
```

Priority categories:

| Score | Priority |
|---:|---|
| 80–100 | Critical |
| 65–79 | Very High |
| 50–64 | High |
| 35–49 | Moderate |
| 0–34 | Watchlist |

## Data foundation status

The current version uses:

- Authoritative global baseline indicators
- Curated source-backed country priority seed data
- Source inventory with URLs
- Data quality checks before scoring

For production research, replace the seed country dataset with official machine-readable downloads from:

- HDX GRFC dataset
- IPC/CH dashboard extracts
- World Bank WDI
- OCHA Financial Tracking Service
- ACLED conflict data
- WFP VAM / HungerMap
- CHIRPS rainfall and MODIS NDVI data

## How to run

```bash
pip install -r requirements.txt
python src/pipeline.py
```

## Key business analyst insight

The strongest project conclusion is:

> Hunger risk is highest where scale and severity overlap. A country may have millions of food-insecure people, but the highest-priority cases are those where acute food insecurity overlaps with child malnutrition, conflict, access restrictions, displacement, and funding gaps.

## Ethical note

This project is for analytics, education, and portfolio demonstration. It is not intended to replace official humanitarian assessments. The pipeline is designed to make source-backed analysis understandable, not to sensationalize suffering.

## Suggested GitHub repo name

`global-hunger-child-malnutrition-analytics`

## Suggested LinkedIn title

**Global Hunger & Child Malnutrition Risk Analytics | Python, BI & Humanitarian Data Storytelling**
