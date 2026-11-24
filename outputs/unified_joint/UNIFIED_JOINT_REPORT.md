# Unified Joint-Effect Analysis

## Dataset
- Total V1 stories: 3888
- Evaluable for defaulting: 2871

## Coverage by dimension
- gender: 957/972 evaluable (98.5%), aligned rate 43.7%
- race: 338/972 evaluable (34.8%), aligned rate 89.1%
- age: 606/972 evaluable (62.3%), aligned rate 91.4%
- occupation: 970/972 evaluable (99.8%), aligned rate 95.8%

## Primary test A: embedding high-similarity (all 3,888 stories, full coverage)

cond         T=0.3, p=1.0  T=1.0, p=0.3  T=1.0, p=0.9  T=1.5, p=1.0
prompt_tier                                                        
implicit             50.8          49.4          52.2          47.4
semi                 51.9          50.3          49.1          48.8

Chi-square: chi2=2.39, df=7, p=0.9350, n=2588

## Primary test B: deterministic defaulting, gender + occupation pooled

cond        T=0.3, p=1.0 T=1.0, p=0.3 T=1.0, p=0.9 T=1.5, p=1.0
prompt_tier                                                    
implicit       76.397516    77.018634    77.777778    77.358491
semi            78.26087    81.012658    77.018634    75.159236

Chi-square: chi2=1.83, df=7, p=0.9687, n=1280

## All-dimension deterministic pool (coverage caveat for race/age)

cond        T=0.3, p=1.0 T=1.0, p=0.3 T=1.0, p=0.9 T=1.5, p=1.0
prompt_tier                                                    
implicit       76.649746    77.777778    77.227723    76.237624
semi           81.623932    82.568807    82.017544    77.272727

Chi-square: chi2=6.45, df=7, p=0.4880

## Stratified by dimension

### gender (n=634)
cond        T=0.3, p=1.0 T=1.0, p=0.3 T=1.0, p=0.9 T=1.5, p=1.0
prompt_tier                                                    
implicit           56.25         55.0    62.962963        61.25
semi               58.75    63.636364        58.75    53.947368
chi2=2.95, p=0.8894, spread implicit 8.0 pp, semi 9.7 pp

### race (n=87)
cond        T=0.3, p=1.0 T=1.0, p=0.3 T=1.0, p=0.9 T=1.5, p=1.0
prompt_tier                                                    
implicit             0.0         25.0    33.333333         25.0
semi           72.222222    72.727273    82.352941    72.222222
chi2=22.07, p=0.0025, spread implicit 33.3 pp, semi 10.1 pp

### age (n=341)
cond        T=0.3, p=1.0 T=1.0, p=0.3 T=1.0, p=0.9 T=1.5, p=1.0
prompt_tier                                                    
implicit       90.322581    85.714286    82.352941    82.857143
semi           94.545455    89.795918         98.0    86.666667
chi2=9.83, p=0.1985, spread implicit 8.0 pp, semi 11.3 pp

### occupation (n=646)
cond        T=0.3, p=1.0 T=1.0, p=0.3 T=1.0, p=0.9 T=1.5, p=1.0
prompt_tier                                                    
implicit       96.296296    98.765432    92.592593    93.670886
semi           97.530864    97.530864    95.061728    95.061728
chi2=6.23, p=0.5126, spread implicit 6.2 pp, semi 2.5 pp

## Gender-only replicate (prior analysis)
chi2=2.95, p=0.8894, n=634

## Interpretation
One pooled chi-square tests whether hyperparameter condition changes defaulting
patterns differently for implicit vs semi-explicit prompts across the full factorial.
Dimension-stratified tables check whether the pooled result is driven by one category.
