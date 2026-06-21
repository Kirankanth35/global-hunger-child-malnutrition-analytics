# Methodology

## Objective

Build a Python-based business analytics pipeline that transforms public humanitarian indicators into a clean prioritization model for hunger and child malnutrition risk.

## What is measured

This project measures:

- Chronic hunger
- Acute food insecurity
- Child stunting
- Child wasting
- Under-5 mortality context
- IPC/CH Phase 5 catastrophic hunger where available
- Drivers such as conflict, food affordability, climate shocks, displacement, access constraints, and funding gaps

## Why not use only starvation deaths?

There is no single perfect global real-time starvation death counter. Malnutrition often kills indirectly by increasing vulnerability to diseases such as pneumonia, diarrhea, malaria, and neonatal complications. Therefore, the correct analytics frame is:

**food insecurity + child malnutrition + mortality context + crisis drivers + response gaps**

## Risk score formula

```text
Risk Score =
0.20 acute burden
+ 0.15 acute prevalence
+ 0.12 IPC/CH Phase 5 population
+ 0.15 child malnutrition risk
+ 0.12 conflict driver
+ 0.08 economic driver
+ 0.06 climate driver
+ 0.06 displacement driver
+ 0.04 access constraint
+ 0.02 funding gap risk
```

## Business analyst interpretation

The model does not claim to predict deaths. It ranks country/territory priority based on observable public risk signals, so decision-makers can ask better questions:

- Where is the crisis largest?
- Where is it most severe?
- What is driving the crisis?
- Which intervention should be prioritized?
- Which data gaps must be fixed before operational decisions?

## Data limitations

The seed dataset is source-backed but intentionally rounded. It is designed for portfolio analytics and reproducible visualization. For operational use, replace it with official machine-readable datasets from HDX/GRFC, IPC/CH, OCHA, ACLED, World Bank and WFP.
