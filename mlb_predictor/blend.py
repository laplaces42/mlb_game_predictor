import pandas as pd
from collections import defaultdict

OFF_COLS = ["avg","obp","slg","woba","wrc_plus","war","k_pct","bb_pct"]
DEF_COLS = ["k_per_9","bb_per_9","hr_per_9","era","fip","owar"]

def blend_stats(game_stats, projection_stats, c_off=60, c_def=40):
    
    a, b = game_stats.index
    game_id = game_stats.at[a, 'game_id']
    date = game_stats.at[a, 'game_date']

    ga = game_stats.at[a, 'games']
    gb = game_stats.at[b, 'games']

    w_a_off, w_b_off = ga/(ga + c_off), gb/(gb + c_off)
    w_a_def, w_b_def = ga/(ga + c_def), gb/(gb + c_def)

    proj = projection_stats.set_index(["team", "year"])
    # proj_a = proj.loc[game_stats.at[a, "offensive_team"]]
    # proj_b = proj.loc[game_stats.at[b, "offensive_team"]]
    # proj_a = proj_a[proj_a['year'] == int(date[:4])]
    # proj_b = proj_b[proj_b['year'] == int(date[:4])]
    # print(proj_a)
    # print(proj_b)

    rows = []

    for i, opp, w_off, w_def in [(a, b, w_a_off, w_b_def), (b, a, w_b_off, w_a_def)]:
        year = pd.to_datetime(game_stats.at[i, 'game_date']).year
        proj_self = proj.loc[(game_stats.at[i, 'offensive_team'], year)]
        proj_opp = proj.loc[(game_stats.at[i, 'defensive_team'], year)]
        row = {
            'game_id': game_id,
            'game_date': date,
            'offensive_team_id': game_stats.at[i, 'offensive_team_id'],
            'offensive_team': game_stats.at[i, 'offensive_team'],
            'defensive_team': game_stats.at[i, 'defensive_team'],
            'games': game_stats.at[i, 'games'],
            'runs_scored': game_stats.at[i, 'runs_scored'],
            'win_flag': game_stats.at[i, 'win_flag']
        }

        for col in OFF_COLS:
            row[col] = w_off * game_stats.at[i, col] + (1 - w_off) * proj_self[col]
        for col in DEF_COLS:
            row[col] = w_def * game_stats.at[i, col] + (1 - w_def) * proj_opp[col]
        
        rows.append(row)

    return pd.DataFrame(rows)
   

