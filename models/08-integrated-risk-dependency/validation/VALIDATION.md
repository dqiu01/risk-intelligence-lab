# Validation — Integrated Risk / Dependency Engine

Synthetic Growing Small Business preset.

Expected loss: $234,452  
VaR95: $548,283  
ES95: $738,510  
VaR diversification benefit: $176,079

## Dependency curve

|   correlation_scale |   expected_loss |   volatility |   var_95 |   var_99 |   es_95 |   reserve_breach_probability |   sum_standalone_var95 |   diversification_benefit_var95 |
|--------------------:|----------------:|-------------:|---------:|---------:|--------:|-----------------------------:|-----------------------:|--------------------------------:|
|                0    |          235109 |       127504 |   464084 |   667057 |  598758 |                     0.225933 |                 724361 |                          260278 |
|                0.25 |          235033 |       130092 |   466974 |   676624 |  605656 |                     0.229817 |                 724361 |                          257387 |
|                0.5  |          234964 |       138263 |   485571 |   705962 |  630659 |                     0.235917 |                 724361 |                          238791 |
|                0.75 |          234920 |       151816 |   512973 |   755529 |  675521 |                     0.24365  |                 724361 |                          211388 |
|                1    |          234921 |       170492 |   553092 |   834542 |  740919 |                     0.251067 |                 724361 |                          171269 |
|                1.25 |          234997 |       194291 |   599054 |   943095 |  825447 |                     0.253017 |                 724361 |                          125307 |

Automated checks cover reproducibility, marginal-mean preservation, tail-contribution reconciliation, dependency-driven volatility/ES increase, and dependency-curve generation.
