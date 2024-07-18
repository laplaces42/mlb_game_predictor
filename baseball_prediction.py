import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, accuracy_score
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import statsapi
import pickle
import time
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

#Dictionary of all active MLB teams
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
}

#Lists of the six divisions andd the teams in each
#al_east = ['Baltimore Orioles', 'New York Yankees', 'Boston Red Sox', 'Tampa Bay Rays', 'Toronto Blue Jays']
#al_west = ['Seattle Mariners', 'Houston Astros', 'Texas Rangers', 'Los Angeles Angels', 'Oakland Athletics']
#al_central = ['Cleveland Guardians', 'Minnesota Twins', 'Kansas City Royals', 'Detroit Tigers', 'Chicago White Sox']
#nl_east = ['Philadelphia Phillies', 'Atlanta Braves', 'New York Mets', 'Washington Nationals', 'Miami Marlins']
#nl_west = ['Los Angeles Dodgers', 'Arizona Diamondbacks', 'San Diego Padres', 'San Francisco Giants', 'Colorado Rockies']
#nl_central = ['Milwaukee Brewers', 'St. Louis Cardinals', 'Pittsburgh Pirates', 'Cincinnati Reds', 'Chicago Cubs']


# Load and preprocess data
data = pd.read_csv('stats.csv')
data = data[data['Date'].str.contains('2024', na=False)]
data = data.reset_index().drop(['index'], axis=1)
data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d')
data['Runs/Game'] = data['Total Runs']/data['Total Games']
data = data.drop(['Total Runs', 'Total Games', 'RBIs', 'Runs Scored', 'Win?'], axis=1)

#Differentiate between hitting statistics and pitching statistics
hitting_stats = ['AVG', 'OBP', 'SLG', 'WRC+', 'WAR', 'K Percentage', 'BB Percentage', 'BSR', 'AVG/5 Players', 'OBP/5 Players', 'SLG/5 Players', 'WAR/5 Players', 'WRC+/5 Players', 'K Percentage/5 Players', 'BB Percentage/5 Players', 'AVG/Week', 'OBP/Week', 'SLG/Week', 'WAR/Week', 'WRC+/Week', 'K Percentage/Week', 'BB Percentage/Week', 'Runs/Game']
pitching_stats = ['Opposing K/9', 'Opposing HR/9', 'Opposing BB/9', 'ERA', 'Opposing War', 'Opposing K/9/5 Players', 'Opposing BB/9/5 Players', 'ERA/5 Players', 'Opposing WAR/5 Players', 'Opposing K/9/Week', 'Opposing BB/9/Week', 'ERA/Week', 'Opposing WAR/Week']

def calculate_moving_averages(stats, team):
    '''
    Generates exponential moving averages for each column in the dataset for a specific team

    Inputs:
    stats -- Statistics for the 2024 season
    team -- The desired team to generate rolling averages for

    Returns:
    team_offensive_stats -- A dataset including the exponential moving averages for the desired team on offense
    team_defensive_stats -- A dataset including the exponential moving averages for the desired team on defense
    '''
    
    #Generates offensive and defensive datasets for the desired team
    team_offensive_stats = pd.DataFrame(stats[stats['Offensive Team'] == team]).reset_index().drop(['index'], axis=1)
    team_defensive_stats = pd.DataFrame(stats[stats['Defensive Team'] == team]).reset_index().drop(['index'], axis=1)
    
    #Calculates the moving average for the team_offensive_stats dataset
    for col in team_offensive_stats.columns:
        if col not in ['Date', 'Offensive Team', 'Defensive Team']:
            team_offensive_stats[f'{col}_EMA'] = team_offensive_stats[col].ewm(span=28, adjust=False).mean()
    
    #Calculates the moving average for the team_defensive_stats dataset
    for col in team_defensive_stats.columns:
        if col not in ['Date', 'Offensive Team', 'Defensive Team']:
            team_defensive_stats[f'{col}_EMA'] = team_defensive_stats[col].ewm(span=28, adjust=False).mean()
            

    return team_offensive_stats, team_defensive_stats

def predict_stats(team_stats, date):
    '''
    Predicts statistics based on the moving averages generated in calculate_moving)averages

    Inputs:
    team_stats -- The dataset with moving averages used to generate statistics from
    date -- The desired date to predict statistics for

    Returns:
    predicted_stats -- The predicted statistics for the given date
    '''

    #Finds the amount of days to generate predicted statistics for
    latest_recorded_date = team_stats.sort_values(['Date'], ascending=False).iloc[0]['Date']
    num_days = (date-latest_recorded_date).days
    
    #Separates the features that will be used to predict
    all_features = [col for col in team_stats if col not in ['Date', 'Offensive Team', 'Defensive Team']]
    predict_features = [feature for feature in all_features if 'SMA' not in feature and 'EMA' not in feature]
    X = team_stats[all_features]
    y = team_stats[predict_features]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    
    #RandomForestRegressor model used to predict statistics
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    #Predictions and metrics to grade accuracy of model
    '''predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions, multioutput='raw_values')
    mae = mean_absolute_error(y_test, predictions, multioutput='raw_values')'''

    #Finds the date range that will be used to label the dataset 
    future_dates = pd.date_range(start=team_stats['Date'].iloc[-1] + pd.Timedelta(days=1), periods=num_days, freq='D')
    future_day_indices = range(len(team_stats), len(team_stats) + num_days)

    #Pulls the very last entry in the dataset to predict statistics from
    last_values = team_stats[all_features].iloc[-1]

    #Create future feature set with exact same order
    future_X = pd.DataFrame(index=future_day_indices)
    for col in all_features:
        future_X[col] = last_values[col]

    #Generates the future statistics for each day in the date range
    future_predictions = []
    for i in range(num_days):
        prediction = model.predict(future_X.iloc[[i]])
        future_predictions.append(prediction[0])
        last_values = pd.Series(prediction[0], index=predict_features)
        for col in all_features:
            if col in predict_features:
                future_X.loc[i+1:, col] = last_values[col]
    
    future_df = pd.DataFrame(future_predictions, columns=predict_features)
    future_df['Date'] = future_dates
    predicted_stats = future_df.iloc[[-1]].reset_index(drop=True)
    
    return predicted_stats

def dataset_maker(home, away, date, stats):
    '''
    Creates two future datasets that will be used to predict outcomes for

    Inputs:
    home -- Home team of the game being predicted
    away -- Away team of the game being predicted
    date -- Date of the game
    stats -- Statistics for the 2024 season

    Returns:
    home_offense -- Data entry for the home team being on offense
    away_offense -- Data entry for the away team being on offense
    '''

    #Generates four datasets with their exponential moving averages included
    home_hitting, home_pitching = calculate_moving_averages(stats, home)
    away_hitting, away_pitching = calculate_moving_averages(stats, away)

    #Modifies the four datasets to have predicted statistics in them
    home_hitting = predict_stats(home_hitting, date)
    home_pitching = predict_stats(home_pitching, date)
    away_hitting = predict_stats(away_hitting, date)
    away_pitching = predict_stats(away_pitching, date)

    #Combines statistics for the home and away teams so that they can be used in the prediction model
    home_offense = pd.concat([home_hitting[hitting_stats], away_pitching[pitching_stats]], axis=1)
    away_offense = pd.concat([away_hitting[hitting_stats], home_pitching[pitching_stats]], axis=1)

    return home_offense, away_offense

#Load the models used to predict game outcomes
with open('win_model.pkl', 'rb') as file:
    win_model = pickle.load(file)

with open('run_model.pkl', 'rb') as file:
    run_model = pickle.load(file)

def main():
    def prediction(date, schedule):
        '''
        Predicts the outcomes of the games from a given schedule

        Inputs:
        date -- The date of the games being predicted
        schedule -- The schedule of games being predicted

        Returns: None
        '''

        #Ensures there are games to predict
        if schedule:
            for game in schedule:
              #Finds and generates the dataset for the home and away teams in the game
              home_team, away_team = mlb_teams[game['home_name']]['abbr'], mlb_teams[game['away_name']]['abbr']
              print(game['away_name'], 'at', game['home_name'])
              home_offense, away_offense = dataset_maker(home_team, away_team, date, data)

              #Predicts the outcomes and runs (if needed) for each team
              home_win, away_win = win_model.predict(home_offense)[0], win_model.predict(away_offense)[0]
              home_runs, away_runs = run_model.predict(home_offense)[0], run_model.predict(away_offense)[0]
              
              #Prints the predicted results of the game
              if home_win > away_win:
                  print(  f"  {game['home_name']} Wins")
                  
              elif home_win < away_win:
                  print(  f"  {game['away_name']} Wins")
                  
              else:
                  if home_runs > away_runs:
                      print(  f"  {game['home_name']} Wins")
                      
                  elif home_runs < away_runs:
                      print(  f"  {game['away_name']} Wins")
                      
                  else:
                      print('Results inconclusive')     
            
            

        else:
            print('No games scheduled for this day.')
            
    def find_date():
        month = input('Enter a month (1-12): ')
        while month not in list(map(str, list(range(1,12)))):
            print('Month must be between 1 and 12')
            month = input('Enter a month (1-12): ')
        
        if int(month) < 10:
            month = '0' + month

        if int(month) in [1,3,5,7,8,10,12]:
            day = input('Enter a day (1-31): ')
            while day not in list(map(str, list(range(1,32)))):
                print('Day must be between 1 and 31')
                day = input('Enter a day (1-31): ')

        
        elif int(month) in [4,6,9,11]:
            day = input('Enter a day (1-30): ')
            while day not in list(map(str, list(range(1,31)))):
                print('Day must be between 1 and 30')
                day = input('Enter a day (1-30): ')

        elif int(month) == 2:
            day = input('Enter a day (1-29): ')
            while day not in list(map(str, list(range(1,30)))):
                print('Day must be between 1 and 29')
                day = input('Enter a day (1-29): ')
        
        if int(day) < 10:
            day = '0' + day
        
        date = datetime.strptime(f'2024-{month}-{day}', '%Y-%m-%d')
        if date < datetime.today():
            print('Cannot predict games in the past.')
            next = input('Press any key to try again, or hit q to quit: ')
            if next == 'q':
                quit
            else:
                os.system('clear')
                return find_date()
        else:
            return date

    print('1. Generate all predictions for a certain date')
    print('2. Generate a prediction for a single game')
    print('3. Generate predictions for a certain team for the rest of the season')
    num = input('Pick from one of the above options: ')
    
    if num == '1':
        date = find_date()
        schedule = statsapi.schedule(date=date.date())
        prediction(date=date, schedule=schedule)
        
        next = input('Press any key to go back to menu, or hit q to quit: ')
        if next == 'q':
            quit
        else:
            os.system('clear')
            main()
    
    if num == '2':
        date = find_date()
        team=statsapi.lookup_team(lookup_value=input('Enter a team name (home or away): '), season=2024)[0]['id']
        schedule = statsapi.schedule(date=date.date(), team=team)
        prediction(date=date, schedule=schedule)
        
        next = input('Press any key to go back to menu, or hit q to quit: ')
        if next == 'q':
            quit
        else:
            os.system('clear')
            main()

    if num == '3':
        team=statsapi.lookup_team(lookup_value=input('Enter a team name (home or away): '), season=2024)[0]['id']
        schedule = statsapi.schedule(start_date=datetime.today().date(), end_date='2024-12-31', team=team)

        for game in schedule:
            prediction(date=datetime.strptime(game['game_date'], '%Y-%m-%d'), schedule=[game])
        
        next = input('Press any key to go back to menu, or hit q to quit: ')
        if next == 'q':
            quit
        else:
            os.system('clear')
            main()

    else:
        print('Invalid option.')
        main()

    
if __name__ == "__main__":
    print('Welcome to the MLB Games Predictor!')
    main()