# Methodology and definitions

## Scope
- Competition: English Premier League first division; 2024/25 and 2025/26, 38 fixtures per Newcastle season.
- Observations: one Newcastle fixture per row (76 rows). The source has 380 league games per season, used to derive the full tables.
- Season-end league rankings: points descending, goal difference descending, goals scored descending (sufficient to determine Newcastle's rank in both years).
- Results: Newcastle's perspective, whether home or away.
- Match ordering: actual fixture date, then matchweek as deterministic tie-breaker (important in postponed matches).
- Source season snapshots are pinned to commit `e6744429ee395bc86f247348c6184bb08d4eb361` (22 Sep 2026 UTC).

## Calculations
- **W/D/L:** scored more, equal, fewer than conceded.
- **Points:** `3 × wins + draws`, per match points 3/1/0.
- **Goal difference:** `goals_for − goals_against`.
- **Win rate:** `wins / matches × 100` (percentage points for difference).
- **Points per match:** `points / matches`.
- **Clean sheet:** `goals_against == 0` (includes scoreless draws).
- **Failed to score:** `goals_for == 0`.
- **Scored/conceded 2+:** `goals_for >= 2` and `goals_against >= 2`.
- **Cumulative points:** running sum of match points by chronological match number.
- **Rolling form:** 5-match rolling average of points; first 4 observations missing, not filled.
- **Venue:** Home/Away, each with 19 games per completed season.
- **First/last half:** first/last 19 Newcastle matches in date order, not Matchweek 1–19 and 20–38.
- **Shared opponent:** team appeared in both league seasons; compare Newcastle's **two matches per season** for each. Exclude promoted/relegated opponents lacking a pair.

## Cleaning decisions
- Use `score.ft` when JSON score is a map; use score values directly when a two-item array.
- Require both final-score values to be nonnegative integers. Reject invalid score shapes instead of silently dropping matches.
- Source `team1` is home, `team2` away; goals are normalized to Newcastle's perspective.
- Remove only a terminal ` FC` for dashboard display; keep original opponent field.
- Parse missing half-time arrays as missing values; do not infer a half-time draw or do halfway analyses.
- Preserve raw score format as an auditable field.
- No estimated, forecast, imputed or synthetic player metrics.

## Reproduce

From repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.analysis --offline    # uses committed source extract; zero network required
pytest -q
python -m src.analysis --refresh    # optional: download pinned complete JSON and regenerate extracts
```

`--refresh` requires internet; `--offline` rebuilds derived tables and visuals from the checked-in 76-row extract and 40-row standings snapshot. The pinned upstream file is never required just to open the HTML dashboard, PNG charts or Excel workbook.

## Licenses
Input data from [OpenFootball/football.json](https://github.com/openfootball/football.json) is CC0-1.0. Project prose, scripts and visual styling are MIT (see `LICENSE`). No official club crest or third-party photos are included.
