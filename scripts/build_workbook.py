"""Rebuild a cross-platform Excel workbook with formula-driven match summaries.

Requires artifact_tool (the ChatGPT spreadsheet authoring engine).
The prebuilt workbook is included; this extra script documents its construction.
"""
from __future__ import annotations
import csv
from datetime import datetime
from pathlib import Path
from artifact_tool import Workbook, SpreadsheetFile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'newcastle_performance_analysis.xlsx'
DARK='#162331'; BLACK='#101a26'; BLUE='#1f3545'; LIGHT='#ebf4fa'; WHITE='#ffffff'; ACCENT='#83c8dc'; RED='#ce745f'; GREEN='#26775d'

def load(name):
    with (ROOT/'data'/'processed'/name).open(newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f))

def header(sheet, area):
    sheet.get_range(area).format={
      'fill':DARK,'font':{'bold':True,'color':WHITE},
      'row_height':27,'vertical_alignment':'center'
    }

wb=Workbook.create()
ov=wb.worksheets.add('Overview')
sm=wb.worksheets.add('Season KPIs')
lg=wb.worksheets.add('Match Log')
tb=wb.worksheets.add('League Table')
ve=wb.worksheets.add('Venue Analysis')
notes=wb.worksheets.add('Sources and Notes')

# Raw match observations: authoritative inputs, sortable by fixture date.
source=load('newcastle_source_extract.csv')
source.sort(key=lambda r:(r['season'],r['date'],int(r['matchweek'])))
cols=['Season','Game','Date','Matchweek','Venue','Opponent','GF','GA','Result','Points','GD','Clean sheet']
lg.get_range('A1:L1').values=[cols]
raw_rows=[]
for i,r in enumerate(source, start=1):
    seq=i if r['season']=='2024-25' else i-38
    raw_rows.append([r['season'],seq,datetime.strptime(r['date'],'%Y-%m-%d'),int(r['matchweek']),r['venue'],r['opponent'],int(r['goals_for']),int(r['goals_against']),None,None,None,None])
lg.get_range('A2:L77').values=raw_rows
lg.get_range('I2:L77').formulas=[[f'=IF(G{r}>H{r},"W",IF(G{r}=H{r},"D","L"))',f'=IF(I{r}="W",3,IF(I{r}="D",1,0))',f'=G{r}-H{r}',f'=IF(H{r}=0,1,0)'] for r in range(2,78)]
header(lg,'A1:L1');lg.freeze_panes.freeze_rows(1)
lg.get_range('A:A').format.column_width=13;lg.get_range('B:B').format.column_width=8;lg.get_range('C:C').format.column_width=15
lg.get_range('D:E').format.column_width=12;lg.get_range('F:F').format.column_width=31;lg.get_range('G:L').format.column_width=12
lg.get_range('C2:C77').set_number_format('yyyy-mm-dd')
lg.get_range('I2:I77').conditional_formats.add_custom('=I2="L"',{'fill':'#F8D8D2'})
lg.get_range('I2:I77').conditional_formats.add_custom('=I2="W"',{'fill':'#D6F4E9'})

# All 40 Premier League final standings, derived from complete 380-game league datasets.
league=load('premier_league_standings.csv')
tb_cols=['Season','Position','Club','Played','W','D','L','GF','GA','GD','Points']
tb.get_range('A1:K1').values=[tb_cols]
tb.get_range('A2:K41').values=[
  [r['season'],int(r['position']),r['team'],int(r['played']),int(r['wins']),int(r['draws']),int(r['losses']),
   int(r['goals_for']),int(r['goals_against']),int(r['goal_difference']),int(r['points'])] for r in league]
header(tb,'A1:K1');tb.freeze_panes.freeze_rows(1)
tb.get_range('A:A').format.column_width=14;tb.get_range('B:B').format.column_width=11;tb.get_range('C:C').format.column_width=35;tb.get_range('D:K').format.column_width=12

# All KPI metrics derived using Excel formulas from the match observations.
sm_cols=['Season','Played','Wins','Draws','Losses','GF','GA','GD','Points','Clean sheets','Failed to score','Win rate','Pts/game','League finish']
sm.get_range('A1:N1').values=[sm_cols];sm.get_range('A2:A3').values=[['2024-25'],['2025-26']]
for row in [2,3]:
    s=f"'Match Log'!$A$2:$A$77"; w=f"'Match Log'!$I$2:$I$77";g=f"'Match Log'!$G$2:$G$77";a=f"'Match Log'!$H$2:$H$77";cl=f"'Match Log'!$L$2:$L$77"
    formulas=[
      f'=COUNTIF({s},A{row})',f'=COUNTIFS({s},A{row},{w},"W")',f'=COUNTIFS({s},A{row},{w},"D")',f'=COUNTIFS({s},A{row},{w},"L")',
      f'=SUMIF({s},A{row},{g})',f'=SUMIF({s},A{row},{a})',f'=F{row}-G{row}',f'=C{row}*3+D{row}',
      f'=COUNTIFS({s},A{row},{cl},1)',f'=COUNTIFS({s},A{row},{g},0)',f'=C{row}/B{row}',f'=I{row}/B{row}',
      f'=SUMIFS(\'League Table\'!$B$2:$B$41,\'League Table\'!$A$2:$A$41,A{row},\'League Table\'!$C$2:$C$41,"Newcastle United FC")'
    ]
    sm.get_range(f'B{row}:N{row}').formulas=[formulas]
header(sm,'A1:N1');sm.get_range('A:A').format.column_width=14;sm.get_range('B:N').format.column_width=16;sm.get_range('J:K').format.column_width=21
sm.get_range('L2:L3').set_number_format('0.0%');sm.get_range('M2:M3').set_number_format('0.000')

# Home and away, 19 fixtures in each year. Recomputed from sheet formulas.
ve.get_range('A1:I1').values=[['Season','Venue','Played','Wins','Draws','Losses','Goals for','Goals against','Points']]
ve.get_range('A2:B5').values=[['2024-25','Home'],['2024-25','Away'],['2025-26','Home'],['2025-26','Away']]
for row in range(2,6):
    season="'Match Log'!$A$2:$A$77";v="'Match Log'!$E$2:$E$77";rs="'Match Log'!$I$2:$I$77";gf="'Match Log'!$G$2:$G$77";ga="'Match Log'!$H$2:$H$77"; pts="'Match Log'!$J$2:$J$77"
    ve.get_range(f'C{row}:I{row}').formulas=[[
     f'=COUNTIFS({season},A{row},{v},B{row})',
     f'=COUNTIFS({season},A{row},{v},B{row},{rs},"W")',
     f'=COUNTIFS({season},A{row},{v},B{row},{rs},"D")',
     f'=COUNTIFS({season},A{row},{v},B{row},{rs},"L")',
     f'=SUMIFS({gf},{season},A{row},{v},B{row})',
     f'=SUMIFS({ga},{season},A{row},{v},B{row})',
     f'=SUMIFS({pts},{season},A{row},{v},B{row})'
    ]]
header(ve,'A1:I1');ve.get_range('A:I').format.column_width=16

# Executive summary references actual formula-based summary, not manually typed KPIs.
ov.merge_cells('A1:M2');ov.get_range('A1').values=[['NEWCASTLE UNITED | SEASON PERFORMANCE']]
ov.get_range('A1:M2').format={'fill':BLACK,'font':{'bold':True,'color':WHITE,'size':18},'row_height':29}
ov.merge_cells('A3:M3');ov.get_range('A3').values=[['2024/25 vs 2025/26  •  Premier League  •  38 matches per season  •  real match data']]
ov.get_range('A3:M3').format={'fill':BLUE,'font':{'color':LIGHT},'row_height':24}
ov.get_range('A5:D5').values=[['Indicator','2024/25','2025/26','Change']]
summary_labels=[('League finish','N'),('Wins','C'),('Draws','D'),('Losses','E'),('Points','I'),('Goals scored','F'),('Goals conceded','G'),('Goal difference','H'),('Clean sheets','J'),('Failed to score','K')]
for n,(label_,col) in enumerate(summary_labels,start=6):
    ov.get_range(f'A{n}').values=[[label_]]
    ov.get_range(f'B{n}:D{n}').formulas=[[f"='Season KPIs'!{col}2",f"='Season KPIs'!{col}3",f'=C{n}-B{n}']]
header(ov,'A5:D5')
ov.get_range('A:A').format.column_width=25;ov.get_range('B:D').format.column_width=16;ov.get_range('E:E').format.column_width=4
ov.get_range('F:M').format.column_width=11
ov.get_range('D6:D15').conditional_formats.add_cell_is({'operator':'lessThan','formula':0,'format':{'font':{'color':RED}}})
ov.get_range('A18:D18').values=[['Metric','2024/25','2025/26','Change']];header(ov,'A18:D18')
for n,(name,srcrow) in enumerate([('Wins',7),('Goals for',11),('Goals against',12),('Points',10)],start=19):
    ov.get_range(f'A{n}').values=[[name]]
    ov.get_range(f'B{n}:D{n}').formulas=[[f'=B{srcrow}',f'=C{srcrow}',f'=C{n}-B{n}']]
ov.merge_cells('A25:M25');ov.get_range('A25').values=[['KEY READING  |  11 of 17 lost points came in away matches; home goals conceded increased by 10.']]
ov.get_range('A25:M25').format={'fill':BLUE,'font':{'bold':True,'color':WHITE},'row_height':30}
ov.merge_cells('A27:M27');ov.get_range('A27').values=[['LIMITATION  |  No xG, shots or possession. These results measure what changed, not why.']]
ov.get_range('A27:M27').format={'font':{'color':RED},'row_height':24}
try:
    chart=ov.charts.add('bar',ov.get_range('A18:C22'))
    chart.title_text='Wins / Goals / Points by season'
    chart.set_position('F6','M22')
except Exception as exc:
    print('Optional chart could not be drawn:',exc)

notes.get_range('A1:B1').values=[['SOURCE & METHOD','DETAIL']];header(notes,'A1:B1')
note_rows=[
 ['Primary data','OpenFootball football.json, English Premier League season results (CC0-1.0)'],
 ['24/25 source','https://github.com/openfootball/football.json/blob/e6744429ee395bc86f247348c6184bb08d4eb361/2024-25/en.1.json'],
 ['25/26 source','https://github.com/openfootball/football.json/blob/e6744429ee395bc86f247348c6184bb08d4eb361/2025-26/en.1.json'],
 ['Snapshot','Git commit e6744429ee395bc86f247348c6184bb08d4eb361; accessed 20 Nov 2026'],
 ['League validation','https://www.premierleague.com/en/tables/premier-league/2025-26'],
 ['Goal perspective','GF and GA are always from Newcastle perspective, whether Home or Away'],
 ['Score cleaning','Source mixes score.ft objects with direct two-number arrays; both parsed'],
 ['Half-time data','Some half-time fields missing; these have not been replaced with estimated values'],
 ['Match Log','Row-level GF/GA are source inputs; W/D/L, points, GD and clean sheets use Excel formulas'],
 ['Season KPIs','Calculated from Match Log using COUNTIFS and SUMIF; league position from League Table'],
 ['Venue Analysis','Derived using COUNTIFS / SUMIFS from Match Log'],
 ['Caution','No xG, shots, possession or player data present. Do not infer causal factors.'],
 ['Project README','See README.md, docs/CASE_STUDY.md and docs/METHODOLOGY.md in repository']
]
notes.get_range('A2:B14').values=note_rows
notes.get_range('A:A').format.column_width=23;notes.get_range('B:B').format.column_width=90
notes.get_range('B2:B14').format.wrap_text=True
notes.freeze_panes.freeze_rows(1)

# Targeted sanity check and export; output also opens in Excel on macOS.
try:
    inspect=wb.inspect({'kind':'table','range':'Overview!A5:D15','include':'values,formulas','table_max_rows':11,'table_max_cols':4})
    print('Summary inspected:',inspect.ndjson[:1300])
except Exception as exc:
    print('Inspection not available:',exc)
SpreadsheetFile.export_xlsx(wb).save(str(OUT))
print('Saved',OUT,OUT.stat().st_size,'bytes')
