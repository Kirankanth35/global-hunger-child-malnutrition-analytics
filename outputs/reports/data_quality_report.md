# Data Foundation Quality Report

This report verifies whether the project data foundation is clean enough to support analysis.

| category     | check_name                                  | status   |   score | detail                               |   weighted_score |
|:-------------|:--------------------------------------------|:---------|--------:|:-------------------------------------|-----------------:|
| Schema       | Required country columns present            | PASS     |     100 | All required columns present.        |              100 |
| Schema       | Required global indicator columns present   | PASS     |     100 | All required global columns present. |              100 |
| Uniqueness   | No duplicate country-year rows              | PASS     |     100 | Duplicate country-year rows: 0       |              100 |
| Completeness | Critical numeric fields complete            | PASS     |     100 | Numeric completeness: 100.0%         |              100 |
| Validity     | Percentages and 1-10 scores in valid ranges | PASS     |     100 | Out-of-range cells: 0                |              100 |
| Traceability | Source URLs available                       | PASS     |     100 | Rows missing source URLs: 0          |              100 |
| Reliability  | High/Medium-High confidence coverage        | PASS     |      80 | High/Medium-High share: 80.0%        |               80 |

## Interpretation

- PASS means the condition is strong enough for portfolio analytics.
- WARN means the project is usable but should be upgraded when official machine-readable data is added.
- FAIL means the pipeline should stop before producing final insights.
