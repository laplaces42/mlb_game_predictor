# MLB Game Predictor
Welcome to the MLB Game Predictor! This project leverages advanced machine learning models to predict the outcomes of MLB games during the 2024 season. The primary aim is to provide accurate game-by-game predictions and season-long projections using a comprehensive set of historical data.

## Key Features
- **Historical Data Utilization:** The models are trained on an extensive dataset that includes team statistics from nearly every game between the 2000 and 2024 seasons and is continuously being updated. This ensures that there is a sufficient amount of data for the models to understand patterns between statistics and outcomes.
- **Comprehensive Team Statistics:** The dataset includes a wide range of team statistics that cover almost every aspect of a baseball game. These encompass both offensive and defensive statistics, as well as season-wide and recent performance for each team.
- **Machine Learning Models:** This project uses Ridge Classifier and Linear Regression models to predict the outcome and scores of games. After testing various models for both outcome and run prediction, these models consistenly performed.
- **Future Statistic Prediction:** This project includes the functionality to predict the statistics for any upcoming game from now until the end of the season using exponential moving averages and past team performance. This allows the model's predictive ability to not be limited to games it has concrete statistics for.

## Data Sources
- [FanGraphs](https://www.fangraphs.com/leaders/major-league) for web scraping all necessary team statistics
- [MLB-StatsAPI](https://github.com/toddrob99/MLB-StatsAPI) for finding schedules for given date ranges
