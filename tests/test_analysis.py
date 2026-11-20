import pandas as pd
import pytest
from src.analysis import DATA, enrich_matches, parse_score, quality_checks, summarize


def test_mixed_score_shape():
    assert parse_score({'score': {'ft': [2, 3]}}) == (2, 3, 'object')
    assert parse_score({'score': [0, 0]}) == (0, 0, 'array')
    with pytest.raises(ValueError):
        parse_score({'score': {'ht': [0, 0]}})


def test_verified_season_totals():
    raw=pd.read_csv(DATA/'newcastle_source_extract.csv')
    table=pd.read_csv(DATA/'premier_league_standings.csv')
    df=enrich_matches(raw)
    checks=quality_checks(raw,df,table)
    assert checks['missing_final_scores']==0
    assert checks['duplicate_matches']==0
    assert checks['score_arrays_newcastle']=={'2024-25':0,'2025-26':4}
    summary=summarize(df).set_index('season')
    for season,w,d,l,gf,ga,pts in [('2024-25',20,6,12,68,47,66),('2025-26',14,7,17,53,55,49)]:
        row=summary.loc[season]
        assert (int(row.wins),int(row.draws),int(row.losses),int(row.goals_for),int(row.goals_against),int(row.points)) == (w,d,l,gf,ga,pts)


def test_home_away_and_chronological_order():
    df=enrich_matches(pd.read_csv(DATA/'newcastle_source_extract.csv'))
    assert all(df.groupby('season').venue.value_counts().eq(19))
    assert df[df.season=='2024-25'].iloc[31].matchweek==29  # postponed fixture was played later
    points=df.groupby(['season','venue']).points.sum()
    assert (points.loc['2024-25','Away'],points.loc['2025-26','Away']) == (28,17)
    assert (points.loc['2024-25','Home'],points.loc['2025-26','Home']) == (38,32)
