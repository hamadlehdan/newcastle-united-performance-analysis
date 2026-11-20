# Case study — Where did Newcastle United's performance go?

**Business question:** How did Newcastle United move from 5th in the Premier League in 2024/25 to 12th in 2025/26, and which observable performance dimensions changed most?

**Audience:** Hiring managers looking for clear data cleaning, descriptive analysis and business-facing storytelling skills. Analysis is restricted to league results; no causal model is attempted.

## Executive findings

| Metric | 2024/25 | 2025/26 | Change |
|:---|---:|---:|---:|
| League finish | 5th | 12th | Down 7 positions |
| Played | 38 | 38 | 0 |
| Wins | 20 | 14 | **−6** |
| Draws | 6 | 7 | +1 |
| Losses | 12 | 17 | +5 |
| Win rate | 52.6% | 36.8% | −15.8 percentage points |
| Points | 66 | 49 | **−17** |
| Points per game | 1.737 | 1.289 | −0.448 |
| Goals scored | 68 | 53 | **−15** |
| Goals conceded | 47 | 55 | **+8** |
| Goal difference | +21 | −2 | **−23** |
| Clean sheets | 13 | 8 | −5 |
| Failed to score | 7 | 9 | +2 |
| Matches conceding at least two | 11 | 17 | +6 |

## Finding 1 — Away attacking output is the clearest results-based weakness

In 2024/25, Newcastle earned **28 points** from 19 away games (8 wins, 4 draws, 7 losses), scoring **28 goals**. In 2025/26, the club earned **17 away points** (4 wins, 5 draws, 10 losses) and scored **17 away goals**. The away-point decline of 11 explains **64.7% of the overall 17-point drop** in arithmetic terms; it does **not** demonstrate a single causal factor. Away goals allowed fell slightly (27 → 25), so the fall in away scoring coincided with the bigger away-results decline.

## Finding 2 — Home defensive output deteriorated

Newcastle conceded **20 goals at home** in 2024/25 versus **30** in 2025/26. Home clean sheets dropped from **8** to **3**. Although home wins also declined (12 → 10), the club still took 32 home points in 2025/26; its away record was the larger source of lost points.

## Finding 3 — The late-season points gap widened

The first 19 chronologically played fixtures yielded **32 versus 26 points**, a decline of 6. The last 19 yielded **34 versus 23 points**, a decline of 11. As a result, the net 17-point difference reflects both a weaker initial half and an even bigger gap in the later half. Chronological match order is used: in 2024/25 Matchweek 29 was played after Matchweek 32.

## Shared-opponent comparison

Only **16 opponents** appeared in both Premier League seasons (excluding Newcastle); each had exactly two games against Newcastle per year. For example, Newcastle earned 6 points against Manchester United in 2024/25 versus 3 in 2025/26, and 3 versus Arsenal compared with 0. These comparisons isolate matching opposition names but **do not** control for changes to coaching, lineups, schedule congestion or player availability. Promoted and relegated clubs are excluded from this comparison rather than assigned synthetic results.

## Data cleansing and validation

The 2025/26 source includes **27 league records** where `score` is a direct `[home, away]` array instead of the usual `{ "ft": [home, away] }` object; **four** affect Newcastle. The parser handles both structures. Five Newcastle records across the two seasons lack half-time scores; these are left **missing**, not assumed to be 0–0. All 76 Newcastle final scores are present.

Automated checks confirm 38 matches and 38 unique matchweeks per season, 20 league clubs per season, no duplicate Newcastle matchweeks, zero missing final goals, and exact agreement with official published final table totals. Both years were compared across 38 matches, not mixed full-season and partial-season periods.

## What this analysis cannot tell us

The supplied data supports results, scorelines, win percentages, clean sheets, goals scored and conceded, league ranking, home/away splits and form. It **does not contain** shots, shots on target, xG, possession, press intensity, injuries, transfers or minutes played, so those metrics were neither calculated nor fabricated. Without additional independently sourced event data, it is not defensible to claim that a specific tactical or personnel factor *caused* the decline.

## Further analysis (outside scope)

To investigate *why* performance changed, a second stage could use independently licensed xG, shots, player availability or line-up data and test whether away chance creation or home defensive shot quality shifted. The existing project should be treated as an evidence-based diagnosis of observable results, not a causal attribution.

**Sources**: [OpenFootball JSON](https://github.com/openfootball/football.json), [24/25 raw](https://github.com/openfootball/football.json/blob/e6744429ee395bc86f247348c6184bb08d4eb361/2024-25/en.1.json), [25/26 raw](https://github.com/openfootball/football.json/blob/e6744429ee395bc86f247348c6184bb08d4eb361/2025-26/en.1.json), [Premier League 2024/25 table](https://www.premierleague.com/en/tables/premier-league/2024-25), [Premier League 2025/26 table](https://www.premierleague.com/en/tables/premier-league/2025-26). Source JSON CC0-1.0. Accessed 20 November 2026.
