#Import necessary libraries
import requests
import time
import statsapi
import pandas as pd
from bs4 import BeautifulSoup
import random
from statistics import mean
import os
from datetime import datetime, timedelta

#Dictionary of all MLB teams from the last 24 years along with their abbreviations and identifying number
mlb_teams = {
    "Arizona Diamondbacks": {'abbr': 'ARI', 'team_num': 15},
    "Atlanta Braves": {'abbr': 'ATL', 'team_num': 16},
    "Baltimore Orioles": {'abbr': 'BAL', 'team_num': 2},
    "Boston Red Sox": {'abbr': 'BOS', 'team_num': 3},
    "Chicago White Sox": {'abbr': 'CHW', 'team_num': 4},
    "Chicago Cubs": {'abbr': 'CHC', 'team_num': 17},
    "Cincinnati Reds": {'abbr': 'CIN', 'team_num': 18},
    "Cleveland Guardians": {'abbr': 'CLE', 'team_num': 5},
    "Colorado Rockies": {'abbr': 'COL', 'team_num': 19},
    "Detroit Tigers": {'abbr': 'DET', 'team_num': 6},
    "Houston Astros": {'abbr': 'HOU', 'team_num': 21},
    "Kansas City Royals": {'abbr': 'KCR', 'team_num': 7},
    "Los Angeles Angels": {'abbr': 'LAA', 'team_num': 1},
    "Los Angeles Dodgers": {'abbr': 'LAD', 'team_num': 22},
    "Miami Marlins": {'abbr': 'MIA', 'team_num': 20},
    "Milwaukee Brewers": {'abbr': 'MIL', 'team_num': 23},
    "Minnesota Twins": {'abbr': 'MIN', 'team_num': 8},
    "New York Yankees": {'abbr': 'NYY', 'team_num': 9},
    "New York Mets": {'abbr': 'NYM', 'team_num': 25},
    "Oakland Athletics": {'abbr': 'OAK', 'team_num': 10},
    "Philadelphia Phillies": {'abbr': 'PHI', 'team_num': 26},
    "Pittsburgh Pirates": {'abbr': 'PIT', 'team_num': 27},
    "San Diego Padres": {'abbr': 'SDP', 'team_num': 29},
    "San Francisco Giants": {'abbr': 'SFG', 'team_num': 30},
    "Seattle Mariners": {'abbr': 'SEA', 'team_num': 11},
    "St. Louis Cardinals": {'abbr': 'STL', 'team_num': 28},
    "Tampa Bay Rays": {'abbr': 'TBR', 'team_num': 12},
    "Texas Rangers": {'abbr': 'TEX', 'team_num': 13},
    "Toronto Blue Jays": {'abbr': 'TOR', 'team_num': 14},
    "Washington Nationals": {'abbr': 'WSN', 'team_num': 24},
    "Montreal Expos": {'abbr': 'MON', 'team_num': 24},
    "Cleveland Indians": {'abbr': 'CLE', 'team_num': 5},
    "Tampa Bay Devil Rays": {'abbr': 'TBD', 'team_num': 12},
    "Anaheim Angels": {'abbr': 'ANA', 'team_num': 1},
    "Florida Marlins": {'abbr': 'FLA', 'team_num': 20},
}

#Empty dictionary where statistics will be stored
stats = {
    'Date': [],
    'Offensive Team': [],
    'Defensive Team': [],
    'Total Games': [],
    'Total Runs': [],
    'RBIs': [],
    'AVG': [],
    'OBP': [],
    'SLG': [],
    'WRC+': [],
    'WAR': [],
    'K Percentage': [],
    'BB Percentage': [],
    'BSR': [],
    'Opposing K/9': [],
    'Opposing HR/9': [],
    'Opposing BB/9': [],
    'ERA': [],
    'Opposing War': [],
    'AVG/5 Players': [],
    'OBP/5 Players': [],
    'SLG/5 Players': [],
    'WAR/5 Players': [],
    'WRC+/5 Players': [],
    'K Percentage/5 Players': [],
    'BB Percentage/5 Players': [],
    'Opposing K/9/5 Players': [],
    'Opposing BB/9/5 Players': [],
    'ERA/5 Players': [],
    'Opposing WAR/5 Players': [],
    'AVG/Week': [],
    'OBP/Week': [],
    'SLG/Week': [],
    'WAR/Week': [],
    'WRC+/Week': [],
    'K Percentage/Week': [],
    'BB Percentage/Week': [],
    'Opposing K/9/Week': [],
    'Opposing BB/9/Week': [],
    'ERA/Week': [],
    'Opposing WAR/Week': [],
    'Runs Scored': [],
    'Win?': [],
}

#Copy of the original stats dictionary to reference
original_stats = stats.copy()

def stats_per_year(year):
    '''
    Builds a dataset that includes statistics for each team and each game for a given year. Web scrapes through FanGraphs.com to pull statistics from variouds pages
    Exports the completed statistics to a CSV file.
    
    Inputs:
    year -- Integer representing the year to pull statistics from

    Returns: None
    '''

    #Generates the regular season schedule for a given year
    schedule = [game for game in statsapi.schedule(start_date=f'{year}-01-01', end_date=f'{year}-12-31') if game['game_type'] == 'R']

    #Initialize opening day value and dates list to iterate through
    opening_day = datetime.strptime(pd.DataFrame(schedule)['game_date'][0], '%Y-%m-%d').date()
    dates = list(set(pd.DataFrame(schedule)['game_date']))
    dates.sort()
    
    for date in dates:
        #Resets stats dictionary before every iteration
        date = datetime.strptime(date, '%Y-%m-%d').date()

        #Used in debugging, can check which day causes function to crash
        print(date)

        #Ensures the date is far enough past opening day to have enough statistics, and exludes statistics from today
        if date >= opening_day + timedelta(weeks=3) and date < datetime.today().date() and str(date) not in list(pd.read_csv('stats.csv')['Date']):

            stats = {
                'Date': [],
                'Offensive Team': [],
                'Defensive Team': [],
                'Total Games': [],
                'Total Runs': [],
                'RBIs': [],
                'AVG': [],
                'OBP': [],
                'SLG': [],
                'WRC+': [],
                'WAR': [],
                'K Percentage': [],
                'BB Percentage': [],
                'BSR': [],
                'Opposing K/9': [],
                'Opposing HR/9': [],
                'Opposing BB/9': [],
                'ERA': [],
                'Opposing War': [],
                'AVG/5 Players': [],
                'OBP/5 Players': [],
                'SLG/5 Players': [],
                'WAR/5 Players': [],
                'WRC+/5 Players': [],
                'K Percentage/5 Players': [],
                'BB Percentage/5 Players': [],
                'Opposing K/9/5 Players': [],
                'Opposing BB/9/5 Players': [],
                'ERA/5 Players': [],
                'Opposing WAR/5 Players': [],
                'AVG/Week': [],
                'OBP/Week': [],
                'SLG/Week': [],
                'WAR/Week': [],
                'WRC+/Week': [],
                'K Percentage/Week': [],
                'BB Percentage/Week': [],
                'Opposing K/9/Week': [],
                'Opposing BB/9/Week': [],
                'ERA/Week': [],
                'Opposing WAR/Week': [],
                'Runs Scored': [],
                'Win?': [],
            }

            #Initializes the daily schedule of games
            daily_schedule = [game for game in statsapi.schedule(date=date) if game['game_type'] == 'R']

            #Hitting statistics for each team from opening day to date
            hitURL = f'https://www.fangraphs.com/leaders/major-league?startdate={opening_day}&enddate={date}&ind=0&qual=0&pageitems=2000000000&season1=&season=&type=8&pos=all&stats=bat&team=0,ts&month=1000'
            hit_page = requests.get(hitURL)
            hit_soup = BeautifulSoup(hit_page.content, "html.parser")
            hit_table = hit_soup.find('div', class_='table-scroll')
            hit_rows = hit_table.find('tbody').find_all('tr')

            #Pitching statistics for each team from opening day to date
            pitchURL = f'https://www.fangraphs.com/leaders/major-league?startdate={opening_day}&enddate={date}&ind=0&qual=0&pageitems=2000000000&season1=&season=&type=8&pos=all&stats=pit&team=0,ts&month=1000'
            pitch_page = requests.get(pitchURL)
            pitch_soup = BeautifulSoup(pitch_page.content, "html.parser")
            pitch_table = pitch_soup.find('div', class_='table-scroll')
            pitch_rows = pitch_table.find('tbody').find_all('tr')

            for game in daily_schedule:
                #Pitching List Structure:
                #[index, team, tg, w, l, sv, g, gs, ip, k/9, bb/9, hr/9, babip, lob%, era, fip, war]
                #['26', 'HOU', '14', '6', '8', '3', '50', '14', '122.0', '6.86', '3.47', '1.77', '.315', '71.7%', '5.61', '5.47', '0.3']

                #Hitting List Structure:
                #[index, team, tg, g, pa, hr, r, rbi, sb, bb%, k%, iso, babip, avg, obp, slg, woba, wrc+, bsr, off, def, war]
                #['27', 'HOU', '14', '163', '531', '19', '77', '73', '8', '10.9%', '18.5%', '.183', '.257', '.236', '.331', '.419', '.330', '87', '-1.6', '-11.6', '0.0', '0.6']
                if game['home_name'] in mlb_teams and game['away_name'] in mlb_teams and game['home_score'] != game['away_score']:
                    
                    #Initializes necessary variables
                    home_team, home_runs, home_num = mlb_teams[game['home_name']]['abbr'], game['home_score'], mlb_teams[game['home_name']]['team_num']
                    away_team, away_runs, away_num = mlb_teams[game['away_name']]['abbr'], game['away_score'],  mlb_teams[game['away_name']]['team_num']

                    #Locates hitting statistics for each team
                    for row in hit_rows:
                        team_cell = row.find('td', {'data-stat': 'Team'})
                        if team_cell and team_cell.text.strip() == home_team:
                            home_hit = [cell.text.strip() for cell in row.find_all('td')]

                        if team_cell and team_cell.text.strip() == away_team:
                            away_hit = [cell.text.strip() for cell in row.find_all('td')]
                    
                    #Locates pitching statistics for each team
                    for row in pitch_rows:
                        team_cell = row.find('td', {'data-stat': 'Team'})
                        if team_cell and team_cell.text.strip() == home_team:
                            home_pitch = [cell.text.strip() for cell in row.find_all('td')]

                        if team_cell and team_cell.text.strip() == away_team:
                            away_pitch = [cell.text.strip() for cell in row.find_all('td')]

                    #Add all data to the stats dictionary
                    stats['Date'].append(date)
                    stats['Date'].append(date)
                    stats['Offensive Team'].append(home_team)
                    stats['Offensive Team'].append(away_team)
                    stats['Defensive Team'].append(away_team)
                    stats['Defensive Team'].append(home_team)
                    stats['Total Games'].append(int(home_hit[2]))
                    stats['Total Games'].append(int(away_hit[2]))
                    stats['Total Runs'].append(int(home_hit[6]))
                    stats['Total Runs'].append(int(away_hit[6]))
                    stats['RBIs'].append(int(home_hit[7]))
                    stats['RBIs'].append(int(away_hit[7]))
                    stats['AVG'].append(float(home_hit[15]))
                    stats['AVG'].append(float(away_hit[15]))
                    stats['OBP'].append(float(home_hit[16]))
                    stats['OBP'].append(float(away_hit[16]))
                    stats['SLG'].append(float(home_hit[17]))
                    stats['SLG'].append(float(away_hit[17]))
                    stats['WRC+'].append(float(home_hit[20]))
                    stats['WRC+'].append(float(away_hit[20]))
                    stats['WAR'].append(float(home_hit[26]))
                    stats['WAR'].append(float(away_hit[26]))
                    stats['K Percentage'].append(float(home_hit[11][:len(home_hit[11])-1])/100)
                    stats['K Percentage'].append(float(away_hit[11][:len(away_hit[11])-1])/100)
                    stats['BB Percentage'].append(float(home_hit[10][:len(home_hit[10])-1])/100)
                    stats['BB Percentage'].append(float(away_hit[10][:len(away_hit[10])-1])/100)
                    stats['BSR'].append(float(home_hit[22]))
                    stats['BSR'].append(float(away_hit[22]))
                    stats['Opposing K/9'].append(float(away_pitch[10]))
                    stats['Opposing K/9'].append(float(home_pitch[10]))
                    stats['Opposing BB/9'].append(float(away_pitch[11]))
                    stats['Opposing BB/9'].append(float(home_pitch[11]))
                    stats['Opposing HR/9'].append(float(away_pitch[12]))
                    stats['Opposing HR/9'].append(float(home_pitch[12]))
                    stats['ERA'].append(float(away_pitch[20]))
                    stats['ERA'].append(float(home_pitch[20]))
                    stats['Opposing War'].append(float(away_pitch[25]))
                    stats['Opposing War'].append(float(home_pitch[25]))
                    stats['Runs Scored'].append(home_runs)
                    stats['Runs Scored'].append(away_runs)
                    stats['Win?'].append(home_runs > away_runs)
                    stats['Win?'].append(home_runs < away_runs)
                    
                    #Takes breaks in between iterations to ensure website doesn't get overloaded
                    #time.sleep(random.uniform(3, 5))

                    #Finds the date a week prior to date
                    game_7 = date - timedelta(days=7)

                    #Hitting statistics for the home team from game_7 to date
                    hit7 = f'https://www.fangraphs.com/leaders/major-league?startdate={game_7}&enddate={date}&ind=0&qual=0&pageitems=2000000000&type=8&pos=all&stats=bat&team={home_num}&season1=&season=&month=1000&sortcol=3&sortdir=default&pagenum=1'
                    hit7_page = requests.get(hit7)
                    hit7_soup = BeautifulSoup(hit7_page.content, "html.parser")
                    hit7_table = hit7_soup.find('div', class_='table-scroll')
                    hit7_rows = hit7_table.find('tbody').find_all('tr')
                    
                    #Pitching statistics for the away team from game_7 to date
                    pitch7 = f'https://www.fangraphs.com/leaders/major-league?startdate={game_7}&enddate={date}&ind=0&qual=0&pageitems=2000000000&type=8&pos=all&stats=pit&team={away_num}&season1=&season=&month=1000&sortcol=7&sortdir=default&pagenum=1'
                    pitch7_page = requests.get(pitch7)
                    pitch7_soup = BeautifulSoup(pitch7_page.content, "html.parser")
                    pitch7_table = pitch7_soup.find('div', class_='table-scroll')
                    pitch7_rows = pitch7_table.find('tbody').find_all('tr')
                    
                    #Initialize lists to hold hitting and pitching statistics for key players
                    hit_stats = []
                    pitch_stats = []
                    
                    #Finds each player that plays for the home team in the hitting statistics
                    for row in hit7_rows:
                        team_cell = row.find('td', {'data-stat': 'Team'})
                        if team_cell and team_cell.text.strip() == home_team:
                            home_hit = [cell.text.strip() for cell in row.find_all('td')]
                            hit_stats.append(home_hit)
                    
                    #Finds each player that plays for the away team in the pitching statistics
                    for row in pitch7_rows:
                        team_cell = row.find('td', {'data-stat': 'Team'})
                        if team_cell and team_cell.text.strip() == away_team:
                            away_pitch = [cell.text.strip() for cell in row.find_all('td')]
                            pitch_stats.append(away_pitch)

                    #Shortens the hitting and pitching lists to the top 5 most active players
                    hit_stats = hit_stats[:5]
                    pitch_stats = pitch_stats[:5]

                    #Calculates averages for the top five players in each category and adds them to the stats dictionary
                    avg_5 = mean([float(num[15]) for num in hit_stats])
                    obp_5 = mean([float(num[16]) for num in hit_stats])
                    slg_5 = mean([float(num[17]) for num in hit_stats])
                    war_5 = mean([float(num[26]) for num in hit_stats])
                    wrc_5 = mean([float(num[20]) for num in hit_stats])
                    k_5 = mean([float(num[11][:len(num[11])-1])/100 for num in hit_stats])
                    bb_5 = mean([float(num[10][:len(num[10])-1])/100 for num in hit_stats])
                    ok_5 = mean([float(num[10]) for num in pitch_stats])
                    obb_5 = mean([float(num[11]) for num in pitch_stats])
                    era_5 = mean([float(num[20]) for num in pitch_stats])
                    owar_5 = mean([float(num[25]) for num in pitch_stats])                  
                    stats['AVG/5 Players'].append(avg_5)
                    stats['OBP/5 Players'].append(obp_5)
                    stats['SLG/5 Players'].append(slg_5)
                    stats['WAR/5 Players'].append(war_5)
                    stats['WRC+/5 Players'].append(wrc_5)
                    stats['K Percentage/5 Players'].append(k_5)
                    stats['BB Percentage/5 Players'].append(bb_5)
                    stats['Opposing K/9/5 Players'].append(ok_5)
                    stats['Opposing BB/9/5 Players'].append(obb_5)
                    stats['ERA/5 Players'].append(era_5)
                    stats['Opposing WAR/5 Players'].append(owar_5)

                    #Takes breaks in between iterations to ensure website doesn't get overloaded
                    #time.sleep(random.uniform(3, 5))
                    
                    #Hitting statistics for the away team from game_7 to date
                    hit7 = f'https://www.fangraphs.com/leaders/major-league?startdate={game_7}&enddate={date}&ind=0&qual=0&pageitems=2000000000&type=8&pos=all&stats=bat&team={away_num}&season1=&season=&month=1000&sortcol=3&sortdir=default&pagenum=1'
                    hit7_page = requests.get(hit7)
                    hit7_soup = BeautifulSoup(hit7_page.content, "html.parser")
                    hit7_table = hit7_soup.find('div', class_='table-scroll')
                    hit7_rows = hit7_table.find('tbody').find_all('tr')
                    
                    #Pitching statistics for the home team from game_7 to date
                    pitch7 = f'https://www.fangraphs.com/leaders/major-league?startdate={game_7}&enddate={date}&ind=0&qual=0&pageitems=2000000000&type=8&pos=all&stats=pit&team={home_num}&season1=&season=&month=1000&sortcol=7&sortdir=default&pagenum=1'
                    pitch7_page = requests.get(pitch7)
                    pitch7_soup = BeautifulSoup(pitch7_page.content, "html.parser")
                    pitch7_table = pitch7_soup.find('div', class_='table-scroll')
                    pitch7_rows = pitch7_table.find('tbody').find_all('tr')
                    
                    #Initialize lists to hold hitting and pitching statistics for key players
                    hit_stats = []
                    pitch_stats = []
                    
                    #Finds each player that plays for the away team in the hitting statistics
                    for row in hit7_rows:
                        team_cell = row.find('td', {'data-stat': 'Team'})
                        if team_cell and team_cell.text.strip() == away_team:
                            away_hit = [cell.text.strip() for cell in row.find_all('td')]
                            hit_stats.append(away_hit)
                    
                    #Finds each player that plays for the home team in the pitching statistics
                    for row in pitch7_rows:
                        team_cell = row.find('td', {'data-stat': 'Team'})
                        if team_cell and team_cell.text.strip() == home_team:
                            home_pitch = [cell.text.strip() for cell in row.find_all('td')]
                            pitch_stats.append(home_pitch)

                    #Shortens the hitting and pitching lists to the top 5 most active players
                    hit_stats = hit_stats[:5]
                    pitch_stats = pitch_stats[:5]

                    #Calculates averages for the top five players in each category and adds them to the stats dictionary
                    avg_5 = mean([float(num[15]) for num in hit_stats])
                    obp_5 = mean([float(num[16]) for num in hit_stats])
                    slg_5 = mean([float(num[17]) for num in hit_stats])
                    war_5 = mean([float(num[26]) for num in hit_stats])
                    wrc_5 = mean([float(num[20]) for num in hit_stats])
                    k_5 = mean([float(num[11][:len(num[11])-1])/100 for num in hit_stats])
                    bb_5 = mean([float(num[10][:len(num[10])-1])/100 for num in hit_stats])
                    ok_5 = mean([float(num[10]) for num in pitch_stats])
                    obb_5 = mean([float(num[11]) for num in pitch_stats])
                    era_5 = mean([float(num[20]) for num in pitch_stats])
                    owar_5 = mean([float(num[25]) for num in pitch_stats]) 
                    stats['AVG/5 Players'].append(avg_5)
                    stats['OBP/5 Players'].append(obp_5)
                    stats['SLG/5 Players'].append(slg_5)
                    stats['WAR/5 Players'].append(war_5)
                    stats['WRC+/5 Players'].append(wrc_5)
                    stats['K Percentage/5 Players'].append(k_5)
                    stats['BB Percentage/5 Players'].append(bb_5)
                    stats['Opposing K/9/5 Players'].append(ok_5)
                    stats['Opposing BB/9/5 Players'].append(obb_5)
                    stats['ERA/5 Players'].append(era_5)
                    stats['Opposing WAR/5 Players'].append(owar_5)

                    #Takes breaks in between iterations to ensure website doesn't get overloaded
                    #time.sleep(random.uniform(3, 5))
                    
                    #Hitting statistics for each team from game_7 to date
                    team_hit = f'https://www.fangraphs.com/leaders/major-league?startdate={game_7}&enddate={date}&ind=0&qual=0&pageitems=2000000000&type=8&pos=all&stats=bat&season1=2000&season=2000&postseason=&month=1000&team=0%2Cts'
                    team_hit_page = requests.get(team_hit)
                    team_hit_soup = BeautifulSoup(team_hit_page.content, "html.parser")
                    team_hit_table = team_hit_soup.find('div', class_='table-scroll')
                    team_hit_rows = team_hit_table.find('tbody').find_all('tr')
                    
                    #Pitching statistics for each team from game_7 to date
                    team_pitch = f'https://www.fangraphs.com/leaders/major-league?startdate={game_7}&enddate={date}&ind=0&qual=0&pageitems=2000000000&type=8&pos=all&stats=pit&season1=2000&season=2000&postseason=&team=0,ts&month=1000'
                    team_pitch_page = requests.get(team_pitch)
                    team_pitch_soup = BeautifulSoup(team_pitch_page.content, "html.parser")
                    team_pitch_table = team_pitch_soup.find('div', class_='table-scroll')
                    team_pitch_rows = team_pitch_table.find('tbody').find_all('tr')
                    
                    #Locates hitting statistics for each team
                    for row in team_hit_rows:
                        team_cell = row.find('td', {'data-stat': 'Team'})
                        if team_cell and team_cell.text.strip() == home_team:
                            home_hit = [cell.text.strip() for cell in row.find_all('td')]

                        if team_cell and team_cell.text.strip() == away_team:
                            away_hit = [cell.text.strip() for cell in row.find_all('td')]
                    
                    #Locates pitching statistics for each team
                    for row in team_pitch_rows:
                        team_cell = row.find('td', {'data-stat': 'Team'})
                        if team_cell and team_cell.text.strip() == home_team:
                            home_pitch = [cell.text.strip() for cell in row.find_all('td')]

                        if team_cell and team_cell.text.strip() == away_team:
                            away_pitch = [cell.text.strip() for cell in row.find_all('td')]

                    #Adds new data to the stats dictionary
                    stats['AVG/Week'].append(float(home_hit[15]))
                    stats['OBP/Week'].append(float(home_hit[16]))
                    stats['SLG/Week'].append(float(home_hit[17]))
                    stats['WAR/Week'].append(float(home_hit[26]))
                    stats['WRC+/Week'].append(float(home_hit[20]))
                    stats['K Percentage/Week'].append(float(home_hit[11][:len(home_hit[11])-1])/100)
                    stats['BB Percentage/Week'].append(float(home_hit[10][:len(home_hit[10])-1])/100)
                    stats['Opposing K/9/Week'].append(float(away_pitch[10]))
                    stats['Opposing BB/9/Week'].append(float(away_pitch[11]))
                    stats['ERA/Week'].append(float(away_pitch[20]))
                    stats['Opposing WAR/Week'].append(float(away_pitch[25]))
                    stats['AVG/Week'].append(float(away_hit[15]))
                    stats['OBP/Week'].append(float(away_hit[16]))
                    stats['SLG/Week'].append(float(away_hit[17]))
                    stats['WAR/Week'].append(float(away_hit[26]))
                    stats['WRC+/Week'].append(float(away_hit[20]))
                    stats['K Percentage/Week'].append(float(away_hit[11][:len(away_hit[11])-1])/100)
                    stats['BB Percentage/Week'].append(float(away_hit[10][:len(away_hit[10])-1])/100)
                    stats['Opposing K/9/Week'].append(float(home_pitch[10]))
                    stats['Opposing BB/9/Week'].append(float(home_pitch[11]))
                    stats['ERA/Week'].append(float(home_pitch[20]))
                    stats['Opposing WAR/Week'].append(float(home_pitch[25]))
            
            #Takes breaks in between iterations to ensure website doesn't get overloaded
            #time.sleep(random.uniform(3, 5))
            
            #Updates existing statistics CSV file with new statistics
            new_stats = pd.DataFrame(stats)
            existing_stats = pd.read_csv('stats.csv')
            updated_stats = pd.concat([existing_stats, new_stats], ignore_index=True)
            updated_stats.to_csv('stats.csv', index=False)


def all_stats():
    '''
    Runs the stats_per_year function from 2000 to 2024.

    Inputs: None

    Returns: None
    '''

    #Iterates through each year from 2000 to 2024
    for year in range(2024, 2025):
        stats_per_year(year)

        #States when a year of statistics has been completed
        os.system('clear')
        print(f'{year} Stats Completed.')

        #Takes breaks in between iterations to ensure website doesn't get overloaded
        #time.sleep(random.uniform(1,3))

#Used to build the entire dataset
#all_stats()
#pd.DataFrame(stats).to_csv('stats.csv')


'''while True:
    try:
        all_stats()
    except Exception as e:
        print(f"Script crashed with error: {e}")
        print("Restarting script...")
        time.sleep(3)'''

stats_per_year(2024)