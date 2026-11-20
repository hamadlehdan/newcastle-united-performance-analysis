# Data dictionary

The raw provider uses **home-perspective** scores; all `newcastle_*.csv` match fields are **Newcastle-perspective** values.

## `data/processed/newcastle_source_extract.csv`

| Field | Type | Meaning / provenance |
|---|---|---|
| `season` | text | `2024-25` or `2025-26` |
| `matchweek` | integer | Original source matchday identifier; not necessarily chronological |
| `date` | ISO date | Fixture date |
| `venue` | category | `Home` if Newcastle was `team1`; otherwise `Away` |
| `opponent` | text | Provider club name (unchanged) |
| `goals_for` | integer | Full-time Newcastle goals |
| `goals_against` | integer | Full-time opposition goals |
| `half_time_for`, `half_time_against` | nullable integer | Provider half-time goals if available; not used in headline metrics |
| `raw_score_format` | category | `object` for `score.ft` or `array` for direct list |

## `data/processed/newcastle_matches.csv`

All source-extract columns, plus:

| Field | Type | Description |
|---|---|---|
| `match_number` | integer | Date-ordered appearance, 1–38 |
| `opponent_clean` | text | Terminal ` FC` removed for shorter labels |
| `result` | category | `W`, `D`, `L` from Newcastle's perspective |
| `points` | integer | 3, 1 or 0 |
| `goal_difference` | integer | Match-level GF − GA |
| `clean_sheet` | binary | 1 if GA = 0 |
| `failed_to_score` | binary | 1 if GF = 0 |
| `conceded_2_plus` | binary | 1 if GA ≥ 2 |
| `scored_2_plus` | binary | 1 if GF ≥ 2 |
| `cumulative_points` | integer | Running league points |
| `cumulative_gd` | integer | Running goal difference |
| `rolling_ppg_5` | nullable float | Mean match points over preceding five matches including current |
| `calendar_month` | text | Year-month of fixture |
| `month_label` | text | Abbreviated calendar month |

## Other files

- `premier_league_standings.csv`: source-derived, final 20-team standings per season; 40 rows.
- `season_summary.csv`: 2-row team KPI summary, with calculated rates and position.
- `venue_summary.csv`: 4 rows, home/away aggregate per season.
- `monthly_summary.csv`: team results grouped by calendar month.
- `half_season_summary.csv`: first/last 19 fixtures in chronological order.
- `opponent_comparison.csv`: only the 16 clubs present in both seasons; per-opponent 2-match points/goals and year-on-year deltas.
- `docs/data_quality.json`: actual automated quality checks, not a mock report.

**Missing values:** A blank half-time field means the data was unavailable in that score schema. Never interpret a blank as zero.
