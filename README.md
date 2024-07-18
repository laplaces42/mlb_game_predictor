# MLB Game Predictor
Welcome to the MLB Game Predictor! This project leverages advanced machine learning models to predict the outcomes of MLB games during the 2024 season. The primary aim is to provide accurate game-by-game predictions and season-long projections using a comprehensive historical dataset.

## Key Features
- **Historical Data Utilization:** The models are trained on an extensive dataset that includes team statistics from nearly every game between the 2000 and 2024 seasons and is continuously updated. This ensures that there is a sufficient amount of data for the models to understand patterns between statistics and outcomes.
- **Comprehensive Team Statistics:** The dataset includes a wide range of team statistics that cover almost every aspect of a baseball game. These encompass both offensive and defensive statistics, as well as season-wide and recent performance for each team.
- **Machine Learning Models:** This project uses Ridge Classifier and Linear Regression models to predict the outcome and scores of games. After testing various models for both outcome and run prediction, these models consistently performed.
- **Future Statistic Prediction:** This project includes the functionality to predict the statistics for any upcoming game from now until the end of the season using exponential moving averages and past team performance. This allows the model's predictive ability to not be limited to games, for it has concrete statistics.

## Data Sources
- [FanGraphs](https://www.fangraphs.com/leaders/major-league) for web scraping all necessary team statistics
- [MLB-StatsAPI](https://github.com/toddrob99/MLB-StatsAPI) for finding schedules for given date ranges

## Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/laplaces42/mlb_game_predictor.git
   cd mlb_game_predictor
   ```
2. **Start a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Open an IDE (Optional)**
   ```bash
   code . #For VSCode
   ```
3. **Install [`requirements.txt`](requirements.txt)**
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run [`baseball_dataset.py`](baseball_dataset.py) to update the dataset with any recent statistics
   ```bash
   python baseball_dataset.py
   ```
2. Run [`baseball_model.py`](baseball_model.py) to train the models with the new data
   ```bash
   python baseball_model.py
   ```
3. Run [`baseball_prediction.py`](baseball_prediction.py) to run the main program and request game predictions
   ```bash
   python baseball_prediction.py
   ```

## Results
The results of this project can be used when the [`baseball_prediction.py`](baseball_prediction.py) script is run.

## Contributions
I am open to all (relevant) contributions! To do so, please fork the repository and submit a pull request with your changes. 

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions or feedback, feel free to reach out!

- **Email:** [laplace.sallis@gmail.com](mailto:laplace.sallis@gmail.com)
- **LinkedIn:** [LaPlace Sallis IV](https://www.linkedin.com/in/laplace-sallis-iv-bbbb602a8/)
- **GitHub:** [laplaces42](https://github.com/laplaces42)

You can also open an issue on this repository if you have any questions or need support.

