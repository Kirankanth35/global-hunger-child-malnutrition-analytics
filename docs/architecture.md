# Pipeline Architecture

```text
Authoritative Sources
    ↓
Seed / Raw Data Layer
    - global_reference_indicators.csv
    - country_priority_seed.csv
    - source_inventory.csv
    - intervention_catalog.csv
    ↓
Validation Layer
    - required columns
    - duplicate checks
    - numeric completeness
    - valid ranges
    - source URL traceability
    ↓
Risk Scoring Layer
    - normalized burden
    - normalized prevalence
    - Phase 5 severity
    - child malnutrition risk
    - driver intensity scores
    ↓
Business Rules Layer
    - recommended intervention assignment
    - priority level assignment
    - regional and intervention summaries
    ↓
Output Layer
    - PNG charts
    - CSV tables
    - Excel dashboard workbook
    - Markdown reports
```

## Why this architecture is recruiter-friendly

It shows the full business analytics workflow:

1. Define the problem
2. Identify reliable sources
3. Validate the data
4. Transform the data
5. Score and prioritize
6. Visualize clearly
7. Generate executive-ready outputs
8. Document assumptions and limitations
