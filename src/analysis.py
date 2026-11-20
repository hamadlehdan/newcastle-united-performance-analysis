"""Newcastle United 2024/25 vs 2025/26 Premier League portfolio.

Data attribution: openfootball/football.json (CC0-1.0).
Run `python -m src.analysis --offline` against committed source extracts,
or `python -m src.analysis --refresh` to fetch and re-extract full source JSON.
"""
from __future__ import annotations
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'processed'
SEASONS = ('2024-25', '2025-26')
SOURCE_COMMIT = 'e6744429ee395bc86f247348c6184bb08d4eb361'
SOURCE = {s: f'https://raw.githubusercontent.com/openfootball/football.json/{SOURCE_COMMIT}/{s}/en.1.json' for s in SEASONS}
TEAM = 'Newcastle United FC'


def parse_score(match: dict) -> tuple[int, int, str]:
    """OpenFootball mixed `score: [h,a]` and `score: {'ft': [h,a]}` shapes."""
    score = match.get('score')
    if isinstance(score, list):
        pair, shape = score, 'array'
    elif isinstance(score, dict):
        pair, shape = score.get('ft'), 'object'
    else:
        raise ValueError(f'Unexpected score field: {score!r}')
    if not (isinstance(pair, list) and len(pair) == 2 and all(type(v) is int and v >= 0 for v in pair)):
        raise ValueError(f'Invalid final score: {score!r}')
    return pair[0], pair[1], shape


def get_remote_seasons() -> dict[str, list[dict]]:
    out = {}
    for season, url in SOURCE.items():
        req = Request(url, headers={'User-Agent': 'Newcastle-portfolio-research/1.0'})
        with urlopen(req, timeout=30) as response:
            payload = json.load(response)
        out[season] = payload['matches']
        assert len(out[season]) == 380, f'{season}: expected 380 league fixtures'
    return out


def reextract(matches_by_season: dict[str, list[dict]]) -> None:
    """Full league fixtures in -> 76 club results and 40 final league-table rows out."""
    records, table_rows = [], []
    for season, matches in matches_by_season.items():
        sums: dict[str, dict] = {}
        for match in matches:
            home, away, fmt = parse_score(match)
            for club, gf, ga in ((match['team1'], home, away), (match['team2'], away, home)):
                r = sums.setdefault(club, dict(team=club, played=0, wins=0, draws=0,
                                                losses=0, goals_for=0, goals_against=0))
                r['played'] += 1
                r['goals_for'] += gf
                r['goals_against'] += ga
                r['wins' if gf > ga else 'losses' if gf < ga else 'draws'] += 1
            if TEAM not in (match['team1'], match['team2']):
                continue
            is_home = match['team1'] == TEAM
            ht = match.get('score', {}).get('ht') if isinstance(match.get('score'), dict) else None
            gf, ga = (home, away) if is_home else (away, home)
            records.append(dict(season=season, matchweek=int(re.search(r'\d+', match['round']).group()),
                                date=match['date'], venue='Home' if is_home else 'Away',
                                opponent=match['team2'] if is_home else match['team1'],
                                goals_for=gf, goals_against=ga,
                                half_time_for=(ht[0] if is_home else ht[1]) if ht else None,
                                half_time_against=(ht[1] if is_home else ht[0]) if ht else None,
                                raw_score_format=fmt))
        assert len(sums) == 20
        ranked = []
        for r in sums.values():
            r['goal_difference'] = r['goals_for'] - r['goals_against']
            r['points'] = 3 * r['wins'] + r['draws']
            ranked.append(r)
        ranked.sort(key=lambda x: (-x['points'], -x['goal_difference'], -x['goals_for'], x['team']))
        for idx, r in enumerate(ranked, start=1):
            table_rows.append(dict(season=season, position=idx, **r))
    DATA.mkdir(exist_ok=True, parents=True)
    pd.DataFrame.from_records(records).sort_values(['season', 'date', 'matchweek']).to_csv(DATA / 'newcastle_source_extract.csv', index=False)
    pd.DataFrame.from_records(table_rows).to_csv(DATA / 'premier_league_standings.csv', index=False)


def enrich_matches(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in ('matchweek', 'goals_for', 'goals_against'):
        df[c] = pd.to_numeric(df[c], errors='raise').astype(int)
    df['date'] = pd.to_datetime(df['date'], errors='raise')
    df = df.sort_values(['season', 'date', 'matchweek']).reset_index(drop=True)
    df['match_number'] = df.groupby('season').cumcount() + 1
    df['opponent_clean'] = df['opponent'].str.replace(r' FC$', '', regex=True)
    df['result'] = np.where(df.goals_for > df.goals_against, 'W', np.where(df.goals_for == df.goals_against, 'D', 'L'))
    df['points'] = np.select([df.result == 'W', df.result == 'D'], [3, 1], default=0)
    df['goal_difference'] = df.goals_for - df.goals_against
    df['clean_sheet'] = (df.goals_against == 0).astype(int)
    df['failed_to_score'] = (df.goals_for == 0).astype(int)
    df['conceded_2_plus'] = (df.goals_against >= 2).astype(int)
    df['scored_2_plus'] = (df.goals_for >= 2).astype(int)
    df['cumulative_points'] = df.groupby('season').points.cumsum()
    df['cumulative_gd'] = df.groupby('season').goal_difference.cumsum()
    df['rolling_ppg_5'] = df.groupby('season').points.transform(lambda s: s.rolling(5, min_periods=5).mean())
    df['calendar_month'] = df.date.dt.strftime('%Y-%m')
    df['month_label'] = df.date.dt.strftime('%b')
    return df


def summarize(matches: pd.DataFrame) -> pd.DataFrame:
    group = matches.groupby('season', sort=True)
    df = group.agg(played=('result', 'size'), wins=('result', lambda x: (x == 'W').sum()),
                   draws=('result', lambda x: (x == 'D').sum()), losses=('result', lambda x: (x == 'L').sum()),
                   goals_for=('goals_for', 'sum'), goals_against=('goals_against', 'sum'),
                   goal_difference=('goal_difference', 'sum'), points=('points', 'sum'),
                   clean_sheets=('clean_sheet', 'sum'), failed_to_score=('failed_to_score', 'sum'),
                   conceded_2_plus=('conceded_2_plus', 'sum'),
                   scored_2_plus=('scored_2_plus', 'sum')).reset_index()
    df['win_rate_pct'] = (100 * df.wins / df.played).round(1)
    df['points_per_match'] = (df.points / df.played).round(3)
    df['goals_for_per_match'] = (df.goals_for / df.played).round(3)
    df['goals_against_per_match'] = (df.goals_against / df.played).round(3)
    return df


def quality_checks(raw: pd.DataFrame, enriched: pd.DataFrame, league: pd.DataFrame) -> dict:
    checks = {}
    checks['seasons'] = sorted(enriched.season.unique().tolist())
    checks['rows_by_season'] = {s: int((enriched.season == s).sum()) for s in SEASONS}
    checks['unique_matchweek_by_season'] = {s: int(enriched.loc[enriched.season == s, 'matchweek'].nunique()) for s in SEASONS}
    checks['score_arrays_newcastle'] = {s: int(((raw.season == s) & (raw.raw_score_format == 'array')).sum()) for s in SEASONS}
    checks['missing_half_time_values'] = {s: int(raw.loc[raw.season == s, 'half_time_for'].isna().sum()) for s in SEASONS}
    checks['missing_final_scores'] = int(raw[['goals_for', 'goals_against']].isna().sum().sum())
    checks['duplicate_matches'] = int(raw.duplicated(['season', 'matchweek']).sum())
    checks['league_teams_per_season'] = {s: int((league.season == s).sum()) for s in SEASONS}
    checks['league_total_played'] = {s: int(league.loc[league.season == s, 'played'].sum()) for s in SEASONS}
    assert checks['seasons'] == list(SEASONS)
    assert all(v == 38 for v in checks['rows_by_season'].values())
    assert all(v == 38 for v in checks['unique_matchweek_by_season'].values())
    assert checks['missing_final_scores'] == checks['duplicate_matches'] == 0
    assert all(v == 20 for v in checks['league_teams_per_season'].values())
    assert all(v == 760 for v in checks['league_total_played'].values())
    for season, expected in {'2024-25':(20,6,12,68,47,66,5), '2025-26':(14,7,17,53,55,49,12)}.items():
        sub = enriched[enriched.season == season]
        st = league[(league.season == season) & league.team.str.contains('Newcastle')].iloc[0]
        actual = ((sub.result == 'W').sum(), (sub.result == 'D').sum(), (sub.result == 'L').sum(),
                  sub.goals_for.sum(), sub.goals_against.sum(), sub.points.sum(), st.position)
        assert tuple(map(int, actual)) == expected, f'{season}: {actual} != {expected}'
    return checks


def generate(base: Path = ROOT, refresh: bool = False) -> dict:
    if refresh:
        reextract(get_remote_seasons())
    raw = pd.read_csv(DATA / 'newcastle_source_extract.csv')
    league = pd.read_csv(DATA / 'premier_league_standings.csv')
    matches = enrich_matches(raw)
    quality = quality_checks(raw, matches, league)
    season = summarize(matches).merge(league.loc[league.team == TEAM, ['season', 'position']], on='season')
    venue = matches.groupby(['season', 'venue'], sort=True).agg(played=('result','size'), wins=('result',lambda x:(x=='W').sum()),
                        draws=('result',lambda x:(x=='D').sum()), losses=('result',lambda x:(x=='L').sum()),
                        gf=('goals_for','sum'),ga=('goals_against','sum'),points=('points','sum'),clean_sheets=('clean_sheet','sum')).reset_index()
    venue['points_per_match'] = (venue.points / venue.played).round(3)
    month = matches.groupby(['season','calendar_month'],sort=True).agg(played=('result','size'),wins=('result',lambda x:(x=='W').sum()),
                       draws=('result',lambda x:(x=='D').sum()), losses=('result',lambda x:(x=='L').sum()),
                       goals_for=('goals_for','sum'),goals_against=('goals_against','sum'),points=('points','sum')).reset_index()
    month['points_per_match']=(month.points/month.played).round(3)
    half = matches.assign(half=np.where(matches.match_number<=19, 'First 19', 'Last 19')).groupby(['season','half']).agg(
        played=('points','size'),wins=('result',lambda x:(x=='W').sum()),points=('points','sum'),gf=('goals_for','sum'),ga=('goals_against','sum')).reset_index()
    opp = matches.groupby(['season','opponent_clean']).agg(points=('points','sum'),gf=('goals_for','sum'),ga=('goals_against','sum'),
                                                      wins=('result',lambda x:(x=='W').sum()),played=('points','size')).reset_index()
    opp_wide=opp.pivot(index='opponent_clean',columns='season',values=['points','gf','ga'])
    opp_wide.columns = [f'{name}_{s}' for name,s in opp_wide.columns]
    opp_wide=opp_wide.dropna().reset_index()
    for m in ['points','gf','ga']:
        opp_wide[f'{m}_delta'] = opp_wide[f'{m}_2025-26'] - opp_wide[f'{m}_2024-25']
    opp_wide=opp_wide.sort_values('points_delta').reset_index(drop=True)
    out=base / 'data' / 'processed'
    for name, frame in [('newcastle_matches.csv',matches),('season_summary.csv',season),
                        ('venue_summary.csv',venue),('monthly_summary.csv',month),
                        ('half_season_summary.csv',half),('opponent_comparison.csv',opp_wide)]:
        frame.to_csv(out/name,index=False, date_format='%Y-%m-%d',float_format='%.3f')
    (base/'docs'/'data_quality.json').write_text(json.dumps(quality,indent=2)+'\n')
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        from .visualize import build_visuals
        build_visuals(matches, season, venue, month, opp_wide, league, base)
    return dict(quality=quality, seasons=season.to_dict(orient='records'), venue=venue.to_dict(orient='records'),
                half=half.to_dict(orient='records'), shared_opponents=len(opp_wide))


def main():
    p=argparse.ArgumentParser(description='Build Newcastle season analysis from real OpenFootball results.')
    p.add_argument('--refresh', action='store_true', help='Download raw OpenFootball match data (internet required).')
    p.add_argument('--offline', action='store_true', help='Use committed verified 76-match extract (default).')
    args=p.parse_args()
    print(json.dumps(generate(refresh=args.refresh),indent=2))

if __name__=='__main__':
    main()
