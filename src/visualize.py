"""Offline visual deliverables for Newcastle portfolio (data only from match results)."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import get_plotlyjs
from plotly.io import to_html

BG='#0c1119'; CARD='#151e2a'; WHITE='#f0f5f8'; MUTED='#9daebf'; OLD='#8ad6e9'; NEW='#e79a82'; GRID='#34404e'; GOLD='#e6c16b'


def configure(fig, height=400):
    fig.update_layout(paper_bgcolor=CARD,plot_bgcolor=CARD, font=dict(family='Arial',color=WHITE,size=12),
                      height=height,margin=dict(l=45,r=25,t=45,b=50),hovermode='x unified',
                      legend=dict(orientation='h',yanchor='bottom',y=1.02,x=0),
                      xaxis=dict(gridcolor=GRID,zeroline=False),yaxis=dict(gridcolor=GRID,zeroline=False))
    return fig


def build_visuals(matches, season, venue, month, opponent, league, root: Path):
    visuals=root/'visuals'; dash=root/'dashboard'
    visuals.mkdir(parents=True,exist_ok=True);dash.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':11, 'axes.facecolor': CARD, 'figure.facecolor': BG,
                         'text.color':WHITE,'axes.labelcolor':WHITE,'xtick.color':MUTED,
                         'ytick.color':MUTED,'axes.edgecolor':GRID,'grid.color':GRID,
                         'savefig.facecolor':BG,'font.family':'DejaVu Sans'})
    by={s:matches.loc[matches.season==s].sort_values('match_number') for s in ('2024-25','2025-26')}
    labels={'2024-25':'2024/25','2025-26':'2025/26'}
    colors={'2024-25':OLD,'2025-26':NEW}
    # 1: executive cover, publication-quality visual
    fig,axs=plt.subplots(2,2,figsize=(15,9))
    fig.subplots_adjust(top=.68,wspace=.24,hspace=.43,bottom=.09,left=.08,right=.97)
    fig.text(.08,.95,'NEWCASTLE UNITED',fontsize=30,color=WHITE,weight='bold')
    fig.text(.08,.902,'THE PERFORMANCE DROP  |  2024/25 vs 2025/26',fontsize=15,color=OLD,weight='bold')
    fig.text(.08,.855,'Match-results analysis  •  76 Premier League fixtures  •  Source: OpenFootball (CC0)',fontsize=11,color=MUTED)
    old,new=season.iloc[0],season.iloc[1]
    for x,name,v1,v2 in [(.08,'WINS',old.wins,new.wins),(.35,'POINTS',old.points,new.points),(.62,'GOAL DIFFERENCE',old.goal_difference,new.goal_difference)]:
        fig.text(x,.805,name,fontsize=10,color=MUTED)
        fig.text(x,.769,f'{v1}  →  {v2}',fontsize=19,color=WHITE,weight='bold')
    ax=axs[0,0]
    for s in by:
        d=by[s];ax.plot(d.match_number,d.cumulative_points,color=colors[s],linewidth=2.8,label=labels[s])
    ax.set(title='Cumulative league points',xlabel='Match played',ylabel='Points',xlim=(1,38),ylim=(0,71));ax.grid(alpha=.28);ax.legend(loc='upper left',frameon=False,labelcolor=WHITE)
    ax=axs[0,1]
    xx=np.arange(4);w=.35
    met=['Wins','Draws','Losses','Clean sheets']
    for i,s in enumerate(('2024-25','2025-26')):
        d=season.loc[season.season==s].iloc[0]
        ax.bar(xx+(i-.5)*w,[d.wins,d.draws,d.losses,d.clean_sheets],width=w,color=colors[s],label=labels[s])
    ax.set(title='Outcomes and clean sheets',xticks=xx,xticklabels=met,ylim=(0,23));ax.grid(axis='y',alpha=.25);ax.set_axisbelow(True)
    ax=axs[1,0]
    for s in by:
        d=by[s];ax.plot(d.match_number,d.rolling_ppg_5,color=colors[s],linewidth=2.6,label=labels[s])
    ax.set(title='Five-match rolling points per match',xlabel='Match played',ylabel='Points per match',xlim=(5,38),ylim=(0,3.1));ax.grid(alpha=.25)
    ax=axs[1,1]
    x=np.arange(2)
    for i,s in enumerate(('2024-25','2025-26')):
        d=venue.loc[venue.season==s].sort_values('venue',ascending=False)
        ax.bar(x+(i-.5)*.34,d.points_per_match.values,width=.34,color=colors[s])
    ax.set(title='Home / away points per match',xticks=x,xticklabels=['Home','Away'],ylim=(0,2.5));ax.grid(axis='y',alpha=.25);ax.set_axisbelow(True)
    fig.savefig(visuals/'executive_overview.png',dpi=170,bbox_inches='tight');plt.close(fig)
    # 2: points progress
    fig,ax=plt.subplots(figsize=(12,5))
    for s in by:
        d=by[s];ax.plot(d.match_number,d.cumulative_points,lw=3.2,color=colors[s],label=labels[s]);
        ax.annotate(str(int(d.cumulative_points.iloc[-1])),(38,d.cumulative_points.iloc[-1]),xytext=(-20,12),textcoords='offset points',fontsize=13,color=colors[s],weight='bold')
    ax.set(xlabel='Chronological match number',ylabel='Cumulative points',title='The 17-point gap across 38 matches',xlim=(1,39),ylim=(0,72));ax.grid(alpha=.23);ax.legend(frameon=False,labelcolor=WHITE)
    fig.tight_layout();fig.savefig(visuals/'cumulative_points.png',dpi=180);plt.close(fig)
    # 3: goal balances
    fig,ax=plt.subplots(figsize=(10,5))
    inds=np.arange(2); width=.35
    for k,s in enumerate(('2024-25','2025-26')):
        d=season.loc[season.season==s].iloc[0]
        for i,(title,num) in enumerate([('Scored',d.goals_for),('Conceded',d.goals_against)]):
            xx=i+(k-.5)*width;ax.bar(xx,num,width,color=colors[s]);ax.text(xx,num+1,str(int(num)),ha='center',color=WHITE,weight='bold')
    ax.set(xticks=inds,xticklabels=['Goals scored','Goals conceded'],ylim=(0,78),title='Goals for fell; goals against rose');ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
    fig.tight_layout();fig.savefig(visuals/'goals_for_against.png',dpi=180);plt.close(fig)
    # Interactive charts
    points=go.Figure()
    for s in by:
        d=by[s];points.add_trace(go.Scatter(x=d.match_number,y=d.cumulative_points,name=labels[s],
                   mode='lines+markers',line=dict(width=3,color=colors[s]),marker=dict(size=4),
                   customdata=np.stack([d.date.dt.strftime('%d %b %Y').values,d.opponent_clean.values,d.result.values],axis=1),
                   hovertemplate='Game %{x} · %{customdata[0]}<br>Opponent: %{customdata[1]}<br>Result: %{customdata[2]}<br>Cumulative points: %{y}<extra></extra>'))
    configure(points,420);points.update_layout(yaxis_title='Cumulative league points',xaxis_title='Matches played')
    progress=go.Figure()
    for s in by:
        d=by[s];progress.add_trace(go.Scatter(x=d.match_number,y=d.rolling_ppg_5,name=labels[s],mode='lines+markers',
                          line=dict(color=colors[s],width=3),marker=dict(size=4),connectgaps=False,
                          hovertemplate='Match %{x}<br>Last 5 games: %{y:.2f} points/match<extra>%{fullData.name}</extra>'))
    configure(progress,400);progress.update_layout(yaxis_title='Points per match · last five',xaxis_title='Chronological match number')
    groups=go.Figure()
    for s in ('2024-25','2025-26'):
        d=season[season.season==s].iloc[0]
        groups.add_trace(go.Bar(x=['Wins','Draws','Losses','Clean sheets','Failed to score'],
             y=[d.wins,d.draws,d.losses,d.clean_sheets,d.failed_to_score],name=labels[s],marker_color=colors[s],
             text=[int(d.wins),int(d.draws),int(d.losses),int(d.clean_sheets),int(d.failed_to_score)],textposition='outside'))
    configure(groups,400);groups.update_layout(barmode='group',yaxis_title='Number of games',yaxis_range=[0,25])
    venues=go.Figure()
    for s in ('2024-25','2025-26'):
        d=venue[venue.season==s].set_index('venue')
        venues.add_trace(go.Bar(x=['Home','Away'],y=[d.loc['Home','points_per_match'],d.loc['Away','points_per_match']],
              name=labels[s],marker_color=colors[s],text=[f"{d.loc[v,'points_per_match']:.2f}" for v in ['Home','Away']],textposition='outside'))
    configure(venues,400);venues.update_layout(barmode='group',yaxis_title='Points per match',yaxis_range=[0,2.5])
    goalfig=go.Figure()
    for s in ('2024-25','2025-26'):
        d=season[season.season==s].iloc[0]
        goalfig.add_trace(go.Bar(x=['Goals scored','Goals conceded'],y=[d.goals_for,d.goals_against],
                                 name=labels[s],marker_color=colors[s],text=[d.goals_for,d.goals_against],textposition='outside'))
    configure(goalfig,400);goalfig.update_layout(barmode='group',yaxis_range=[0,80])
    opp=opponent.sort_values('points_delta')
    oppfig=go.Figure(go.Bar(x=opp.points_delta,y=opp.opponent_clean,orientation='h',
                 marker_color=[NEW if a<0 else OLD if a>0 else MUTED for a in opp.points_delta],
                 hovertemplate='%{y}<br>Points difference: %{x:+.0f}<extra></extra>'))
    configure(oppfig,600);oppfig.update_layout(showlegend=False,xaxis_title='Change in points across two head-to-head league fixtures',
                                      yaxis=dict(autorange='reversed',gridcolor=GRID),margin=dict(l=155,r=20,t=20,b=60))
    pfig={
      'points':points,'progress':progress,'results':groups,'venues':venues,'goals':goalfig,'opponents':oppfig
    }
    plots={name:to_html(fig,full_html=False,include_plotlyjs=False,config={'displayModeBar':False,'responsive':True}) for name,fig in pfig.items()}
    entries=[]
    for _,r in matches.sort_values(['season','match_number']).iterrows():
        entries.append({'season':r.season,'date':r.date.strftime('%Y-%m-%d'),'match':int(r.match_number),
                        'week':int(r.matchweek),'venue':r.venue,'opponent':r.opponent_clean,
                        'gf':int(r.goals_for),'ga':int(r.goals_against),'result':r.result,'points':int(r.points)})
    figures='\n'.join([f'<article class="plot-card" id="{key}"><h3>{title}</h3><p>{subtitle}</p>{plots[key]}</article>' for key,title,subtitle in [
       ('points','Cumulative points','The complete 38-game trajectory; follow how the gap opens.'),
       ('results','Results and consistency','Wins, draws, losses, clean sheets and scoreless games.'),
       ('goals','Attacking and defensive output','Total league goals for and against — not xG.'),
       ('venues','Home versus away','Comparable 19-home and 19-away fixtures in both seasons.'),
       ('progress','Five-game rolling form','Only starts at game 5; the horizontal axis is chronological play order.'),
       ('opponents','Shared-opponent points swing','Only clubs Newcastle faced in both campaigns; two fixtures per club.')]])
    cards=[]
    old,new=season.iloc[0],season.iloc[1]
    for name,a,b,unit in [('LEAGUE FINISH',int(old.position),int(new.position),'place'),('WINS',int(old.wins),int(new.wins),'matches'),('POINTS',int(old.points),int(new.points),'points'),('GOAL DIFFERENCE',int(old.goal_difference),int(new.goal_difference),'goals')]:
        signed=(lambda v:f'{v:+d}' if v else '0')(b-a)
        cards.append(f'<div class="kpi"><small>{name}</small><strong>{a} <span>→</span> {b}</strong><em>{signed} {unit}</em></div>')
    js_rows=json.dumps(entries,separators=(',',':'))
    html=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Newcastle United | 2024/25 vs 2025/26</title>
<style>
:root{{--bg:{BG};--card:{CARD};--text:{WHITE};--muted:{MUTED};--line:{GRID};--a:{OLD};--b:{NEW}}}
*{{box-sizing:border-box}}body{{background:var(--bg);color:var(--text);margin:0;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}}
main{{max-width:1280px;margin:auto;padding:38px 26px 70px}}header{{border-bottom:1px solid var(--line);padding-bottom:30px}}
.eyebrow{{letter-spacing:.18em;font-size:11px;color:var(--a);font-weight:800}}h1{{font-size:clamp(36px,6vw,65px);letter-spacing:-.05em;margin:12px 0}}.sub{{max-width:800px;color:var(--muted);line-height:1.7}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:26px 0}}.kpi{{padding:23px;background:var(--card);border:1px solid var(--line);border-radius:14px}}
.kpi small{{display:block;color:var(--muted);font-size:11px;letter-spacing:.1em;font-weight:700}}.kpi strong{{display:block;font-size:clamp(20px,2.5vw,31px);margin:11px 0}}.kpi span{{color:#8b96a3}}.kpi em{{font-size:12px;font-style:normal;color:var(--b)}}
.section-head{{margin:45px 0 18px}}h2{{font-size:26px;margin:0 0 10px}}h3{{font-size:18px;margin:0 0 6px}}p{{line-height:1.65}}.section-head p,.plot-card p{{color:var(--muted);font-size:13px;margin:0 0 12px}}
.plots{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}}.plot-card{{min-width:0;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px}}
.plots .plot-card:first-child,.plots .plot-card:last-child{{grid-column:1/-1}}.plotly-graph-div{{width:100%!important}}.insights{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}.insight{{background:#111d27;padding:22px;border-left:3px solid var(--a);border-radius:8px}}
.insight b{{font-size:16px}}.insight p{{font-size:14px;color:var(--muted)}}.table-wrap{{overflow-x:auto;border:1px solid var(--line);border-radius:12px}}table{{border-collapse:collapse;width:100%;font-size:13px}}th,td{{text-align:left;padding:11px 14px;border-bottom:1px solid #293647;white-space:nowrap}}th{{background:#1e2c3b;color:#dae3eb;position:sticky;top:0}}tbody tr:hover{{background:#202b39}}.w{{color:#86dbbb;font-weight:700}}.l{{color:#e89c89;font-weight:700}}.d{{color:#d2c08d;font-weight:700}}
.filters{{display:flex;flex-wrap:wrap;gap:8px;margin:15px 0}}select,input{{background:#182330;border:1px solid var(--line);color:var(--text);padding:10px 12px;border-radius:7px;font-size:13px}}
.foot{{border-top:1px solid var(--line);margin-top:45px;padding-top:20px;color:var(--muted);font-size:13px}}a{{color:var(--a)}}
@media(max-width:800px){{.kpis,.insights,.plots{{grid-template-columns:1fr 1fr}}.plots .plot-card{{grid-column:1/-1}}}}@media(max-width:550px){{.kpis,.insights{{grid-template-columns:1fr}}main{{padding:22px 12px}}.plot-card{{padding:10px}}}}
</style><script>{get_plotlyjs()}</script></head><body><main>
<header><div class="eyebrow">PREMIER LEAGUE · DATA ANALYTICS CASE STUDY</div><h1>THE PERFORMANCE DROP<span style="color:var(--a)">.</span></h1>
<p class="sub">Newcastle United, 2024/25 compared with 2025/26. A reproducible, league-results-based investigation into a fall from fifth to twelfth place. 76 actual league fixtures. No hypothetical metrics.</p></header>
<section class="kpis">{''.join(cards)}</section>
<div class="section-head"><h2>Where did the points go?</h2><p>All charts are interactive. Hover for fixture details and click a legend label to isolate a season.</p></div>
<section class="plots">{figures}</section>
<div class="section-head"><h2>Three evidence-based findings</h2></div>
<section class="insights"><div class="insight"><b>1. Away goals dried up</b><p>Away goals scored fell from 28 to 17 (−11), and away points fell from 28 to 17. That accounted for 11 of the 17 total lost points.</p></div>
<div class="insight"><b>2. Home defending worsened</b><p>Home goals conceded rose from 20 to 30, while home clean sheets fell from 8 to 3. Away goals conceded actually declined slightly (27 to 25).</p></div>
<div class="insight"><b>3. A fall in performance, not just rank</b><p>Wins dropped from 20 to 14. League points dropped from 66 to 49; position slid from fifth to twelfth. The source does not establish why.</p></div></section>
<div class="section-head"><h2>Explore the 76 results</h2><p>Filter the underlying verified match-level observations; score is always Newcastle first.</p></div>
<div class="filters"><select id="season"><option value="">Both seasons</option><option value="2024-25">2024/25</option><option value="2025-26">2025/26</option></select><select id="venue"><option value="">Home & away</option><option>Home</option><option>Away</option></select><select id="result"><option value="">All outcomes</option><option value="W">Win</option><option value="D">Draw</option><option value="L">Loss</option></select><input type="search" id="q" placeholder="Search opponents…" aria-label="Search opponent"/></div>
<div class="table-wrap"><table><thead><tr><th>Season</th><th>Game</th><th>Date</th><th>Venue</th><th>Opponent</th><th>Score</th><th>Result</th><th>Pts</th></tr></thead><tbody id="table"></tbody></table></div><p id="count" style="color:var(--muted);font-size:12px"></p>
<footer class="foot"><strong>Source / reproducibility:</strong> <a href="https://github.com/openfootball/football.json" target="_blank" rel="noreferrer">OpenFootball football.json</a>,
<a href="https://github.com/openfootball/football.json/blob/master/2024-25/en.1.json" target="_blank" rel="noreferrer">2024/25</a> and
<a href="https://github.com/openfootball/football.json/blob/master/2025-26/en.1.json" target="_blank" rel="noreferrer">2025/26</a> (CC0-1.0).
League results only: these data cannot establish changes in xG, shots, possession, injuries or the causal reason for decline. Half-time values are omitted from headline analysis because some source records lack them. Original score-format variations were normalized and audited. For reproducible code, consult the project README.</footer>
</main><script>const records={js_rows};const byId=x=>document.getElementById(x);
function esc(x){{return String(x).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}}
function draw(){{const ss=byId('season').value,v=byId('venue').value,r=byId('result').value,q=byId('q').value.toLowerCase().trim();
const f=records.filter(x=>(!ss||x.season===ss)&&(!v||x.venue===v)&&(!r||x.result===r)&&(!q||x.opponent.toLowerCase().includes(q)));
byId('table').innerHTML=f.map(x=>`<tr><td>${{esc(x.season)}}</td><td>${{x.match}}</td><td>${{x.date}}</td><td>${{x.venue}}</td><td>${{esc(x.opponent)}}</td><td>${{x.gf}}–${{x.ga}}</td><td class="${{x.result.toLowerCase()}}">${{x.result==='W'?'Win':x.result==='L'?'Loss':'Draw'}}</td><td>${{x.points}}</td></tr>`).join('');byId('count').textContent=`Showing ${{f.length}} of ${{records.length}} real fixtures`;}}
for(const id of ['season','venue','result','q'])byId(id).addEventListener(id==='q'?'input':'change',draw);draw();</script>
</body></html>'''
    (dash/'index.html').write_text(html,encoding='utf-8')
    # Dashboard HTML and PNG files are written without console chatter (keeps JSON run output valid).
