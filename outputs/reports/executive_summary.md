# Global Hunger & Child Malnutrition Analytics — Executive Summary

## Data Foundation Check

Foundation readiness score: **97.1/100**.

This means the project has a strong source-backed foundation, while still allowing future replacement of seed country data with official API/HDX extracts.

## Core Global Signals

- **People experiencing chronic hunger / undernourishment**: 673.0 million people (2024) — SOFI 2025 / FAO-WFP-UNICEF-WHO-IFAD
- **Global hunger estimate lower bound**: 638.0 million people (2024) — SOFI 2025 / UNICEF Data
- **Global hunger estimate upper bound**: 720.0 million people (2024) — SOFI 2025 / UNICEF Data
- **Moderate or severe food insecurity**: 2300.0 million people (2024) — SOFI 2025 / UNICEF Data
- **Unable to afford a healthy diet**: 2600.0 million people (2024) — SOFI 2025 / UNICEF Data
- **Acute food insecurity in food-crisis contexts**: 295.3 million people (2024) — GRFC 2025 / WFP
- **Countries/territories covered by GRFC acute food insecurity**: 53.0 count (2024) — GRFC 2025 / WFP
- **Increase in acute food insecurity vs 2023**: 13.7 million people (2024) — GRFC 2025 / WFP
- **Share of assessed population in high acute food insecurity**: 22.6 percent (2024) — GRFC 2025 / UNICEF Press Release
- **Children under 5 stunted**: 150.2 million children (2024) — UNICEF-WHO-World Bank JME 2025 / WHO
- **Children under 5 wasted**: 42.8 million children (2024) — UNICEF-WHO-World Bank JME 2025 / WHO
- **Children under 5 overweight**: 35.5 million children (2024) — UNICEF-WHO-World Bank JME 2025 / WHO
- **Children acutely malnourished in food-crisis contexts**: 35.5 million children (2025) — GRFC 2025 / WFP
- **Children severely acutely malnourished in food-crisis contexts**: 10.0 million children (2025) — GRFC 2025 / WFP
- **Under-5 deaths**: 4.9 million deaths (2024) — WHO / UN IGME
- **Neonatal deaths**: 2.3 million deaths (2024) — WHO / UN IGME
- **Under-5 mortality rate**: 37.4 deaths per 1000 live births (2024) — WHO / UN IGME
- **Under-5 deaths linked to undernutrition**: 45.0 percent approx (2024) — UNICEF Nutrition

## Top Priority Countries/Territories

| country                          |   risk_score | priority_level   |   acute_food_insecurity_m | recommended_intervention                                                            |
|:---------------------------------|-------------:|:-----------------|--------------------------:|:------------------------------------------------------------------------------------|
| Sudan                            |         85.4 | Critical         |                      24.6 | Negotiated humanitarian access + emergency food assistance + local partner delivery |
| Gaza Strip                       |         71.8 | Very High        |                       2.1 | Negotiated humanitarian access + emergency food assistance + local partner delivery |
| Yemen                            |         64.9 | High             |                      18.1 | Negotiated humanitarian access + emergency food assistance + local partner delivery |
| Nigeria                          |         63.8 | High             |                      30.6 | Negotiated humanitarian access + emergency food assistance + local partner delivery |
| Democratic Republic of the Congo |         63.8 | High             |                      27.7 | Negotiated humanitarian access + emergency food assistance + local partner delivery |

## Business Analyst Insight

The highest-risk cases are not only large by population burden; they combine scale, high prevalence, conflict/access constraints, child malnutrition risk, displacement, and funding gaps. The business analytics value is turning these signals into a ranked action portfolio instead of a passive dashboard.

## Recommended Strategy

| recommended_intervention                                                            |   countries |   acute_food_insecurity_m |   avg_risk_score |
|:------------------------------------------------------------------------------------|------------:|--------------------------:|-----------------:|
| Negotiated humanitarian access + emergency food assistance + local partner delivery |          17 |                     201.7 |             54.9 |
| Emergency agricultural support + drought-resilient seeds + water/irrigation support |           3 |                      32.4 |             37.7 |

## Source Inventory

| source_name                       | source_type                           | source_url                                                                                           |
|:----------------------------------|:--------------------------------------|:-----------------------------------------------------------------------------------------------------|
| SOFI 2025                         | UN annual report                      | https://data.unicef.org/resources/sofi-2025/                                                         |
| Global Report on Food Crises 2025 | Consensus humanitarian report         | https://www.wfp.org/publications/global-report-food-crises-grfc                                      |
| GRFC 2025 September Update        | Consensus humanitarian update         | https://knowledge4policy.ec.europa.eu/publication/global-report-food-crises-2025-september-update_en |
| IPC/CH Dashboard                  | IPC/CH official dashboard             | https://www.ipcinfo.org/ipcinfo-website/ipc-dashboard/en/                                            |
| UNICEF-WHO-World Bank JME 2025    | Inter-agency malnutrition estimates   | https://www.who.int/data/gho/data/themes/topics/joint-child-malnutrition-estimates-unicef-who-wb     |
| WHO/UN IGME Child Mortality 2026  | UN mortality estimates                | https://www.who.int/news-room/fact-sheets/detail/child-mortality-under-5-years                       |
| UNICEF Child Nutrition            | UNICEF data portal                    | https://data.unicef.org/topic/nutrition/child-nutrition/                                             |
| HDX GRFC Dataset                  | Machine-readable humanitarian dataset | https://data.humdata.org/dataset/fsin-grfc                                                           |
| World Bank Data360 GRFC           | Machine-readable GRFC subset          | https://data360.worldbank.org/en/dataset/FSIN_GRFC                                                   |
| OCHA Financial Tracking Service   | Humanitarian funding data             | https://fts.unocha.org/                                                                              |
| ACLED                             | Conflict event data                   | https://acleddata.com/                                                                               |
| World Bank WDI                    | Development indicators                | https://databank.worldbank.org/source/world-development-indicators                                   |