import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, RidgeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, accuracy_score
from sklearn.preprocessing import MinMaxScaler
import pickle
#import baseball_dataset

#Ensure the dataset is completely up to date
#baseball_dataset.stats_per_year(2024)

# Load and preprocess data
data = pd.read_csv('stats.csv')
data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
data['Runs/Game'] = data['Total Runs']/data['Total Games']
data = data.drop_duplicates(keep='first')
#data['L10'] = data['Win?'].rolling(window=10, min_periods=1).sum()

#Differentiate between hitting statistics and pitching statistics
hitting_stats = ['AVG', 'OBP', 'SLG', 'WRC+', 'WAR', 'K Percentage', 'BB Percentage', 'BSR', 'AVG/5 Players', 'OBP/5 Players', 'SLG/5 Players', 'WAR/5 Players', 'WRC+/5 Players', 'K Percentage/5 Players', 'BB Percentage/5 Players', 'AVG/Week', 'OBP/Week', 'SLG/Week', 'WAR/Week', 'WRC+/Week', 'K Percentage/Week', 'BB Percentage/Week', 'Runs/Game']
pitching_stats = ['Opposing K/9', 'Opposing HR/9', 'Opposing BB/9', 'ERA', 'Opposing War', 'Opposing K/9/5 Players', 'Opposing BB/9/5 Players', 'ERA/5 Players', 'Opposing WAR/5 Players', 'Opposing K/9/Week', 'Opposing BB/9/Week', 'ERA/Week', 'Opposing WAR/Week']

train = data.sample(frac=0.8, random_state=42)
test = data.drop(train.index)

#Separate between X and y datasets
features = hitting_stats + pitching_stats
X_train = train.drop(['Runs Scored', 'Win?', 'Date', 'Offensive Team', 'Defensive Team', 'Total Games', 'Total Runs', 'RBIs'], axis=1)
X_train = X_train[features]
X_test = test.drop(['Runs Scored', 'Win?', 'Date', 'Offensive Team', 'Defensive Team', 'Total Games', 'Total Runs', 'RBIs'], axis=1)
X_test = X_test[features]
y_train = train['Win?']
y_test = test['Win?']

#Initialize and train the model to predict team wins
win_model = RidgeClassifier()
win_model.fit(X_train, y_train)
predictions = win_model.predict(X_test)

print(accuracy_score(y_test, predictions))

#Download the win model
with open('win_model.pkl', 'wb') as file:
    pickle.dump(win_model, file)

#Initialize and train the model to predict team runs
run_model = LinearRegression()
y_train = train['Runs Scored']
y_test = test['Runs Scored']
run_model.fit(X_train, y_train)
predictions = run_model.predict(X_test)

#Download the run model
with open('run_model.pkl', 'wb') as file:
    pickle.dump(run_model, file)

print(mean_absolute_error(y_test, predictions))
print(mean_squared_error(y_test, predictions))
print(r2_score(y_test, predictions))

