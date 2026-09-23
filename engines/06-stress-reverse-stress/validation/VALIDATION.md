# Validation — Stress & Reverse Stress Testing

Synthetic Growing Small Business preset.

## Forward scenarios

| scenario   |   normalized_stress |     modeled_loss |   capacity_usage | capacity_breached   |
|:-----------|--------------------:|-----------------:|-----------------:|:--------------------|
| Mild       |                0.25 | 674375           |         0.561979 | False               |
| Moderate   |                0.5  |      1.5275e+06  |         1.27292  | True                |
| Severe     |                0.75 |      2.55938e+06 |         2.13281  | True                |
| Extreme    |                1    |      3.77e+06    |         3.14167  | True                |

## Reverse stress

Success: True  
Loss at boundary: $1,200,000  
Risk capacity: $1,200,000  
Weighted distance: 0.9120

| factor                       |   normalized_shock |   adverse_change_pct |
|:-----------------------------|-------------------:|---------------------:|
| Demand decline               |           0.5911   |              26.5995 |
| Margin compression           |           0.389198 |              11.6759 |
| Input-cost shock             |           0.285044 |              11.4017 |
| Funding-cost shock           |           0.161683 |              11.3178 |
| Customer concentration event |           0.429259 |              25.7556 |

Automated checks verify monotonic loss, boundary feasibility, capacity-distance ordering, ordered forward scenarios, and impossible-threshold handling.
