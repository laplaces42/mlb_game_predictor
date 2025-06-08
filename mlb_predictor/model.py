from .blend import OFF_COLS, DEF_COLS
from .scale import fit_standardizer, standardize
import pandas as pd
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

ALPHA_OFF = 5.0
ALPHA_DEF = 5.0
SCALE_COLS = OFF_COLS + DEF_COLS

class _BaseModel:
    target: str
    features: list[str]
    def __init__(self, alpha):
        self.alpha = alpha
        self._scaler_params = None
        self._regr = None

    def fit(self, df):
        X = df[self.features]
        y = df[self.target]

        self._scaler_params = fit_standardizer(X, self.features)
        X_scaled = standardize(X, self._scaler_params)
        self._regr = LinearRegression().fit(X_scaled, y)
        # self._regr = Ridge(alpha=self.alpha).fit(X_scaled, y)

        return self
    
    def predict(self, df):
        X = df[self.features]
        X_scaled = standardize(X, self._scaler_params)

        return self._regr.predict(X_scaled)
    
class OffensiveModel(_BaseModel):
    target = 'runs_scored'
    features = SCALE_COLS

    def __init__(self, alpha=ALPHA_OFF):
        super().__init__(alpha)
        
class DefensiveModel(_BaseModel):
    target = 'runs_allowed'
    features = SCALE_COLS

    def __init__(self, alpha=ALPHA_DEF):
        super().__init__(alpha)
        
def train_models(df, train_end):
    train = df[df['game_date'] < train_end]
    off_model = OffensiveModel().fit(train)
    def_df = train.copy()
    def_df = (
        def_df
        .assign(
            runs_allowed =                    
            def_df.groupby(["game_id", "game_date"])["runs_scored"]
                .transform(lambda s: s.iloc[::-1].values)
        )
    )
    def_model = DefensiveModel().fit(def_df.drop(columns=['runs_scored']))
    return off_model, def_model

def predict_matchup(row_home, row_away, off_model, def_model):
    exp_runs_home = off_model.predict(pd.DataFrame([row_home]))[0] + def_model.predict(pd.DataFrame([row_away]))[0]
    exp_runs_away = off_model.predict(pd.DataFrame([row_away]))[0] + def_model.predict(pd.DataFrame([row_home]))[0]
    return {
        row_home['offensive_team']: exp_runs_home,
        row_away['offensive_team']: exp_runs_away
    }

# ───────────────────────────────────────────────────────────────────────────────
def evaluate_offence(model: OffensiveModel, test_df: pd.DataFrame) -> dict[str, float]:
    """RMSE / MAE / R² for runs-scored predictions on the test set."""
    y_true = test_df["runs_scored"]
    y_pred = model.predict(test_df)
    return {
        "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
        "mae" : mean_absolute_error(y_true, y_pred),
        "r2"  : r2_score(y_true, y_pred),
    }


def evaluate_defence(model: DefensiveModel, test_df: pd.DataFrame) -> dict[str, float]:
    """
    Build runs_allowed column (opponent’s runs_scored),
    then compute regression metrics for the defence model.
    """
    test_df = test_df.copy()
    test_df["runs_allowed"] = (
        test_df.groupby(["game_id", "game_date"])["runs_scored"]
               .transform(lambda s: s.iloc[::-1].values)
    )
    y_true = test_df["runs_allowed"]
    y_pred = model.predict(test_df.drop(columns=["runs_scored"]))
    return {
        "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
        "mae" : mean_absolute_error(y_true, y_pred),
        "r2"  : r2_score(y_true, y_pred),
    }

def evaluate_win_prob(off_model: OffensiveModel,
                      def_model: DefensiveModel,
                      test_df: pd.DataFrame) -> dict[str, float]:
    """
    Turns the two regressors into a game-level win predictor,
    then reports classification accuracy and Brier score.
    """
    # 1️⃣ split the two rows of every game
    g = test_df.groupby(["game_id", "game_date"])
    home_rows = g.nth(0).copy()
    away_rows = g.nth(1).copy()

    # 2️⃣ expected runs for each side
    exp_home = (off_model.predict(home_rows) +
                def_model.predict(away_rows.drop(columns=["runs_scored"])))
    exp_away = (off_model.predict(away_rows) +
                def_model.predict(home_rows.drop(columns=["runs_scored"])))

    run_diff = exp_home - exp_away
    sigma_hat = np.std(off_model.predict(home_rows) - home_rows["runs_scored"])
    win_prob_home = 0.5 * (1 + np.tanh(run_diff / (np.sqrt(2)*sigma_hat)))  # logistic-ish

    # 3️⃣ actual result: 1 if home won
    home_won = home_rows["runs_scored"].values > away_rows["runs_scored"].values

    acc   = np.mean((win_prob_home > 0.5) == home_won)
    brier = np.mean((win_prob_home - home_won) ** 2)
    return {"accuracy": acc, "brier": brier}