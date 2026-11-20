# Tableau Public — suggested extension

The project can be used in Tableau on macOS with no SQL. Tableau Public is not automatically embedded in this offline portfolio; **no published Tableau dashboard is claimed**.

1. Connect to `data/processed/newcastle_matches.csv` as a text file.
2. Ensure `date` is Date, `match_number` and goals are Number (Whole), `points` is Number (Whole), `season` and `venue` are Dimensions.
3. Sheet **Season trends**: Columns `match_number`, Rows `SUM(points)` as a Running Total, Color `season`. Use table calculation partitioned by `season`.
4. Sheet **Goals**: Columns `season`, Rows `SUM(goals_for)` and `SUM(goals_against)` using Measure Names/Values.
5. Sheet **Venue**: Columns `venue`, Rows `AVG(points)`, Color `season` (each season has 19 Home and 19 Away observations).
6. Sheet **Form**: Columns `match_number`, Rows `AVG(points)` with a moving average (previous 4, current), Color `season`.
7. Sheet **Match Explorer**: `date`, `season`, `venue`, `opponent_clean`, `goals_for`, `goals_against`, `result`, `points`; add Season and Venue as filters.
8. Create one dashboard titled **Newcastle 2024/25 vs 2025/26**, arrange overview → trends → diagnostics. Cite both OpenFootball raw links and list the data limitations.

**Caution:** For a matched-opponent view, use `opponent_comparison.csv` directly; promoted/relegated clubs cannot be compared head-to-head across both campaigns.
