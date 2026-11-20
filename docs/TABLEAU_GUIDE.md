# Tableau Public — suggested extension

The project can be used in Tableau on macOS without writing SQL. No published Tableau dashboard is claimed.

1. Connect to `data/processed/newcastle_matches.csv` as a text file.
2. Set `date` to Date; `match_number`, `points` and goal columns to numeric; `season` and `venue` to Dimensions.
3. **Season trends:** Columns `match_number`, Rows `SUM(points)` as a running total, Colour `season`. Partition the calculation by season.
4. **Goals:** Columns `season`, Rows `SUM(goals_for)` and `SUM(goals_against)` using Measure Names/Values.
5. **Venue:** Columns `venue`, Rows `AVG(points)`, Colour `season`.
6. **Form:** Columns `match_number`, Rows `AVG(points)` with a moving average (previous 4, current), Colour `season`.
7. **Match explorer:** Display `date`, `season`, `venue`, `opponent_clean`, `goals_for`, `goals_against`, `result`, `points`; add filters.
8. Create a dashboard titled **Newcastle 2024/25 vs 2025/26**, arranging overview, trends, diagnostics and match table.

**Caution:** This is match-score data, not xG or possession data. Comparing common opponents is possible via `data/processed/opponent_comparison.csv`; promoted/relegated clubs are not paired.
