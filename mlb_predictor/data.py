# Import necessary libraries
import requests
import statsapi
import pandas as pd
from bs4 import BeautifulSoup
import supabase
from datetime import datetime
import os
from collections import defaultdict

sb = supabase.Client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

ALT_ABBR = {
    "Arizona Diamondbacks": {'ARI', 'AZ'},
    "Atlanta Braves": {'ATL'},
    "Baltimore Orioles": {'BAL'},
    "Boston Red Sox": {'BOS'},
    "Chicago White Sox": {'CHW', 'CWS'},
    "Chicago Cubs": {'CHC'},
    "Cincinnati Reds": {'CIN'},
    "Cleveland Guardians": {'CLE', 'IND'},
    "Colorado Rockies": {'COL'},
    "Detroit Tigers": {'DET'},
    "Houston Astros": {'HOU'},
    "Kansas City Royals": {'KCR', 'KC'},
    "Los Angeles Angels": {'LAA', 'ANA'},
    "Los Angeles Dodgers": {'LAD', 'LA'},
    "Miami Marlins": {'MIA', 'FLA'},
    "Milwaukee Brewers": {'MIL'},
    "Minnesota Twins": {'MIN'},
    "New York Yankees": {'NYY'},
    "New York Mets": {'NYM'},
    "Oakland Athletics": {'OAK'},
    "Athletics": {'OAK', 'ATH'},
    "Philadelphia Phillies": {'PHI'},
    "Pittsburgh Pirates": {'PIT'},
    "San Diego Padres": {'SDP', 'SD'},
    "San Francisco Giants": {'SFG', 'SF'},
    "Seattle Mariners": {'SEA'},
    "St. Louis Cardinals": {'STL'},
    "Tampa Bay Rays": {'TBR', 'TB', 'TBD'},
    "Texas Rangers": {'TEX'},
    "Toronto Blue Jays": {'TOR'},
    "Washington Nationals": {'WSN', 'WSH', 'MON'},
    "Montreal Expos": {'MON'},
    "Cleveland Indians": {'CLE', 'IND'},
    "Tampa Bay Devil Rays": {'TBD'},
    "Anaheim Angels": {'ANA'},
    "Florida Marlins": {'FLA'},
}

ALIASES = {
    "Arizona Diamondbacks": {'Arizona Diamondbacks'},
    "Atlanta Braves": {'Atlanta Braves'},
    "Baltimore Orioles": {'Baltimore Orioles'},
    "Boston Red Sox": {'Boston Red Sox'},
    "Chicago White Sox": {'Chicago White Sox'},
    "Chicago Cubs": {'Chicago Cubs'},
    "Cincinnati Reds": {'Cincinnati Reds'},
    "Cleveland Guardians": {'Cleveland Guardians', 'Cleveland Indians'},
    "Colorado Rockies": {'Colorado Rockies'},
    "Detroit Tigers": {'Detroit Tigers'},
    "Houston Astros": {'Houston Astros'},
    "Kansas City Royals": {'Kansas City Royals'},
    "Los Angeles Angels": {'Los Angeles Angels', 'Anaheim Angels'},
    "Los Angeles Dodgers": {'Los Angeles Dodgers'},
    "Miami Marlins": {'Miami Marlins', 'Florida Marlins'},
    "Milwaukee Brewers": {'Milwaukee Brewers'},
    "Minnesota Twins": {'Minnesota Twins'},
    "New York Yankees": {'New York Yankees'},
    "New York Mets": {'New York Mets'},
    "Athletics": {'Oakland Athletics', 'Athletics'},
    "Philadelphia Phillies": {'Philadelphia Phillies'},
    "Pittsburgh Pirates": {'Pittsburgh Pirates'},
    "San Diego Padres": {'San Diego Padres'},
    "San Francisco Giants": {'San Francisco Giants'},
    "Seattle Mariners": {'Seattle Mariners'},
    "St. Louis Cardinals": {'St. Louis Cardinals'},
    "Tampa Bay Rays": {'Tampa Bay Rays', 'Tampa Bay Devil Rays'},
    "Texas Rangers": {'Texas Rangers'},
    "Toronto Blue Jays": {'Toronto Blue Jays'},
    "Washington Nationals": {'Washington Nationals', 'Montreal Expos', 'MON'},
}

ALIAS_FLAT = {alias: canon for canon, aliases in ALIASES.items() for alias in aliases}

def get_stats(opening_day, date):

    def to_float(x, default=0.0):
        try:
            return float(x.strip('%'))
        except (TypeError, ValueError, AttributeError):
            return default

    def api_to_fg(team_name, keys):
        for abbr in ALT_ABBR[team_name]:
            if abbr in keys:
                return abbr
        return None

    stats = {
        'game_id': [],
        'offensive_team_id': [],
        'game_date': [],
        'offensive_team': [],
        'defensive_team': [],
        'games': [],
        'avg': [],
        'obp': [],
        'slg': [],
        'woba': [],
        'wrc_plus': [],
        'war': [],
        'k_pct': [],
        'bb_pct': [],
        'k_per_9': [],
        'bb_per_9': [],
        'hr_per_9': [],
        'era': [],
        'fip': [],
        'owar': [],
        'runs_scored': [],
        'win_flag': [],
    }

    # Hitting statistics for each team from opening day to date
    hitURL = f'https://www.fangraphs.com/leaders/major-league?startdate={opening_day}&enddate={date}&ind=0&qual=0&pageitems=2000000000&season1=&season=&type=8&pos=all&stats=bat&team=0,ts&month=1000'
    hit_page = requests.get(hitURL)
    hit_soup = BeautifulSoup(hit_page.content, "html.parser")
    hit_table = hit_soup.find('div', class_='table-scroll')
    hit_rows = hit_table.find('tbody').find_all('tr')
    hit_map = {(row.find('td', {'data-stat': 'Team'})).text.strip(): {cell.attrs.get('data-stat'): cell.text.strip() for cell in row.find_all('td') if cell.attrs.get('data-stat')} for row in hit_rows}

    # Pitching statistics for each team from opening day to date
    pitchURL = f'https://www.fangraphs.com/leaders/major-league?startdate={opening_day}&enddate={date}&ind=0&qual=0&pageitems=2000000000&season1=&season=&type=8&pos=all&stats=pit&team=0,ts&month=1000'
    pitch_page = requests.get(pitchURL)
    pitch_soup = BeautifulSoup(pitch_page.content, "html.parser")
    pitch_table = pitch_soup.find('div', class_='table-scroll')
    pitch_rows = pitch_table.find('tbody').find_all('tr')
    pitch_map = {(row.find('td', {'data-stat': 'Team'})).text.strip(): {cell.attrs.get('data-stat'): cell.text.strip() for cell in row.find_all('td') if cell.attrs.get('data-stat')} for row in pitch_rows}

    schedule = statsapi.schedule(date=date)
    for game in schedule:
        if game['game_type'] != 'R' or game['status'] != 'Final':
            continue

        home_id, home_team, home_runs = game['home_id'], game['home_name'], game['home_score']
        away_id, away_team, away_runs = game['away_id'], game['away_name'], game['away_score']

        home_hit = hit_map.get(api_to_fg(home_team, set(hit_map.keys())), {})
        away_hit = hit_map.get(api_to_fg(away_team, set(hit_map.keys())), {})
        home_pitch = pitch_map.get(api_to_fg(home_team, set(pitch_map.keys())), {})
        away_pitch = pitch_map.get(api_to_fg(away_team, set(pitch_map.keys())), {})
        if not home_hit or not away_hit or not home_pitch or not away_pitch:
            print(f"Missing data for game {game['game_id']} on {game['game_date'][:10]} between {home_team} and {away_team}. Skipping...")
            print(f"Home Hit: {home_hit}, Away Hit: {away_hit}, Home Pitch: {home_pitch}, Away Pitch: {away_pitch}")
            continue

        # Home team as offensive
        stats['game_id'].append(game['game_id'])
        stats['offensive_team_id'].append(home_id)
        stats['game_date'].append(game["game_date"][:10])
        stats['offensive_team'].append(ALIAS_FLAT.get(home_team, home_team))
        stats['defensive_team'].append(ALIAS_FLAT.get(away_team, away_team))
        stats['games'].append(to_float(home_hit.get('TG', 0)))
        stats['avg'].append(to_float(home_hit.get('AVG', '0.000')))
        stats['obp'].append(to_float(home_hit.get('OBP', '0.000')))
        stats['slg'].append(to_float(home_hit.get('SLG', '0.000')))
        stats['woba'].append(to_float(home_hit.get('wOBA', '0.000')))
        stats['wrc_plus'].append(to_float(home_hit.get('wRC+', '0')))
        stats['war'].append(to_float(home_hit.get('WAR', '0.0')))
        stats['k_pct'].append(to_float(home_hit.get('K%', '0.000'))/100)
        stats['bb_pct'].append(to_float(home_hit.get('BB%', '0.000'))/100)
        stats['k_per_9'].append(to_float(home_pitch.get('K/9', '0.0')))
        stats['bb_per_9'].append(to_float(home_pitch.get('BB/9', '0.0')))
        stats['hr_per_9'].append(to_float(home_pitch.get('HR/9', '0.0')))
        stats['era'].append(to_float(home_pitch.get('ERA', '0.00')))
        stats['fip'].append(to_float(home_pitch.get('FIP', '0.00')))
        stats['owar'].append(to_float(home_pitch.get('WAR', '0.0')))
        stats['runs_scored'].append(home_runs)
        stats['win_flag'].append(home_runs > away_runs)

        # Away team as offensive
        stats['game_id'].append(game['game_id'])
        stats['offensive_team_id'].append(away_id)
        stats['game_date'].append(game["game_date"][:10])
        stats['offensive_team'].append(ALIAS_FLAT.get(away_team, away_team))
        stats['defensive_team'].append(ALIAS_FLAT.get(home_team, home_team))
        stats['games'].append(to_float(away_hit.get('TG', 0)))
        stats['avg'].append(to_float(away_hit.get('AVG', '0.000')))
        stats['obp'].append(to_float(away_hit.get('OBP', '0.000')))
        stats['slg'].append(to_float(away_hit.get('SLG', '0.000')))
        stats['woba'].append(to_float(away_hit.get('wOBA', '0.000')))
        stats['wrc_plus'].append(to_float(away_hit.get('wRC+', '0')))
        stats['war'].append(to_float(away_hit.get('WAR', '0.0')))
        stats['k_pct'].append(to_float(away_hit.get('K%', '0.000'))/100)
        stats['bb_pct'].append(to_float(away_hit.get('BB%', '0.000'))/100)
        stats['k_per_9'].append(to_float(away_pitch.get('K/9', '0.0')))
        stats['bb_per_9'].append(to_float(away_pitch.get('BB/9', '0.0')))
        stats['hr_per_9'].append(to_float(away_pitch.get('HR/9', '0.0')))
        stats['era'].append(to_float(away_pitch.get('ERA', '0.00')))
        stats['fip'].append(to_float(away_pitch.get('FIP', '0.00')))
        stats['owar'].append(to_float(away_pitch.get('WAR', '0.0')))
        stats['runs_scored'].append(away_runs)
        stats['win_flag'].append(home_runs < away_runs)

    return pd.DataFrame(stats)

def generate_latest_stats(start_year, push_to_supabase=False):
    all_data = []
    page = 0
    page_size = 1000

    while True:
        request = (
            sb.table("all_mlb_data")
            .select("*")
            .gte("game_date", datetime.strptime(f"{start_year}-01-01", "%Y-%m-%d").date())
            .range(page * page_size, (page + 1) * page_size - 1)
            .execute()
        )
        data = request.data
        if not data:
            break
        data = pd.DataFrame(data)
        data['offensive_team'] = data['offensive_team'].apply(lambda x: ALIAS_FLAT.get(x, x))
        data['defensive_team'] = data['defensive_team'].apply(lambda x: ALIAS_FLAT.get(x, x))

        data = data.to_dict(orient='records')
        if push_to_supabase:
            # Use upsert to replace existing entries with matching primary key or unique constraint
            response = (sb.table("latest_data").upsert(data).execute())
        all_data.extend(data)
        if len(data) < page_size:
            break
        page += 1

    if not all_data:
        print("No data found for the specified date range.")
        return None
    else:
        
        return all_data


def make_season_totals(year, push_to_supabase=False):
    season_totals = defaultdict(list)
    raw_data = pd.DataFrame(generate_latest_stats(year, push_to_supabase=False))
    raw_data = raw_data[raw_data['game_date'] < "2025-01-01"]
    raw_data.sort_values(by=['game_date'], inplace=True, ascending=True)
    for y in range(year, 2025):
        current = raw_data[(raw_data['game_date'] < f"{y+1}-01-01") & (raw_data['game_date'] >= f"{y}-01-01")]
        if current.empty:
            continue
        teams = current['offensive_team'].unique()
        for team in teams:
            offense = current[current['offensive_team'] == team]
            defense = current[current['defensive_team'] == team]
            season_totals['year'].append(y)
            season_totals['team'].append(ALIAS_FLAT.get(team, team))
            season_totals['avg'].append(offense['avg'].mean())
            season_totals['obp'].append(offense['obp'].mean())
            season_totals['slg'].append(offense['slg'].mean())
            season_totals['woba'].append(offense['woba'].mean())
            season_totals['wrc_plus'].append(offense['wrc_plus'].mean())
            season_totals['war'].append(offense['war'].mean())
            season_totals['k_pct'].append(offense['k_pct'].mean())
            season_totals['bb_pct'].append(offense['bb_pct'].mean())
            season_totals['k_per_9'].append(defense['k_per_9'].mean())
            season_totals['bb_per_9'].append(defense['bb_per_9'].mean())
            season_totals['hr_per_9'].append(defense['hr_per_9'].mean())
            season_totals['era'].append(defense['era'].mean())
            season_totals['fip'].append(defense['fip'].mean())
            season_totals['owar'].append(defense['owar'].mean())

    if push_to_supabase:
        
        # Convert defaultdict to list of dictionaries for upsert
        season_totals_list = []
        for i in range(len(season_totals['year'])):
            record = {}
            for key in season_totals.keys():
                record[key] = season_totals[key][i]

            season_totals_list.append(record)
        
        # Batch upsert in chunks of 1000
        batch_size = 1000
        for i in range(0, len(season_totals_list), batch_size):
            batch = season_totals_list[i:i+batch_size]
            response = sb.table("season_totals").upsert(batch).execute()
        

    return dict(season_totals)

def get_table(table_name):
    page = 0
    page_size = 1000
    all_data = []
    while True:
        request = (
            sb.table(table_name)
            .select("*")
            .range(page * page_size, (page + 1) * page_size - 1)
            .execute()
        )
        data = request.data
        if not data:
            break
        all_data.extend(data)
        if len(data) < page_size:
            break
        page += 1

    return pd.DataFrame(all_data)


# df = generate_latest_stats(2010, push_to_supabase=True)
# df = pd.DataFrame(df)
# print(df)
# df.to_csv("test.csv", index=False)

# df = pd.read_csv("test.csv")
# df['offensive_team'] = df['offensive_team'].apply(lambda x: ALIAS_FLAT.get(x, x))
# print(df)
make_season_totals(2007, push_to_supabase=True)

# Script for processing MLB stats from 2000 to 2025
# while True:
#     try:   
#         years_file = 'years_completed.json'
#         if os.path.exists(years_file):
#             with open(years_file, 'r') as f:
#                 years_completed = json.load(f).get('years_completed', [])
#         else:
#             years_completed = []
#         for year in range(2000, 2026):
#             if year in years_completed:
#                 print(f"Skipping {year}, already processed.")
#                 continue
#             schedule = [game for game in statsapi.schedule(start_date=f'{year}-01-01', end_date=f'{year}-12-31') if game['game_type'] == 'R']
#             opening_day = datetime.strptime(pd.DataFrame(schedule)['game_date'][0], '%Y-%m-%d').date()
#             dates = list(set(pd.DataFrame(schedule)['game_date']))
#             dates.sort()
#             for date in dates:
#                 big_data = pd.read_csv("STATSFR.csv")
#                 date = datetime.strptime(date, '%Y-%m-%d').date()
#                 if date >= datetime.now().date():
#                     print("All Dates Processed.")
#                     break
#                 if date < opening_day or str(date) in big_data['Date'].values:
#                     print(f"Skipping {date}, already processed or before opening day.")
#                     continue
#                 print(f"Processing {date}...")
#                 stats_df = get_stats(opening_day, date)
                
#                 big_data = pd.concat([big_data, stats_df], ignore_index=True)
#                 big_data.to_csv("STATSFR.csv", index=False)
#                 # print(stats_df.head())
            
#             years_completed.append(year)
#             with open(years_file, 'w') as f:
#                 json.dump({'years_completed': years_completed}, f)
            
#             os.system('clear')
#             print(f'{year} Stats Completed.')

#                 # big_data = pd.concat([big_data, stats_df], ignore_index=True)
#     except Exception as e:
#         print(f"Error: {e}. Retrying in 3 seconds...")
#         time.sleep(3)

# df = pd.read_csv("STATSFR.csv")
# duplicates = df[df.duplicated(subset=["game_id", "offensive_team_id", "game_date"], keep=False)]

# if not duplicates.empty:
#     print("Duplicate entries found for the same 'game_id' and 'offensive_team_id':")
#     print(duplicates)
# else:
#     print("No duplicate entries found for 'game_id' and 'offensive_team_id'.")
