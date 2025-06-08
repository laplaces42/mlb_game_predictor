from mlb_predictor.projections import batch_marcel_projections
from mlb_predictor.blend import blend_stats
from mlb_predictor.model import SCALE_COLS
from mlb_predictor.data import get_table
from mlb_predictor.model import train_models, evaluate_defence, evaluate_offence, evaluate_win_prob
import supabase
import pandas as pd
import os


# season_df = get_table("season_totals")
# years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
# projections = batch_marcel_projections(season_df, SCALE_COLS, years)

# latest_df = get_table("latest_data")
# blended_df = latest_df.groupby(["game_id", "game_date"]).apply(
#     lambda x: blend_stats(x, projections)
# ).reset_index(drop=True)

# blended_df.to_csv("blended_stats.csv", index=False)
blended_df = pd.read_csv("blended_stats.csv")
cutoff = "2024-01-01"
train_df = blended_df[blended_df["game_date"] < cutoff]
test_df  = blended_df[blended_df["game_date"] >= cutoff]

off_m, def_m = train_models(blended_df, train_end=cutoff)
off_metrics  = evaluate_offence(off_m, test_df)
def_metrics  = evaluate_defence(def_m, test_df)
win_metrics  = evaluate_win_prob(off_m, def_m, test_df)


print("Offence  RMSE: {rmse:.2f}  MAE: {mae:.2f}  R²: {r2:.3f}".format(**off_metrics))
print("Defence  RMSE: {rmse:.2f}  MAE: {mae:.2f}  R²: {r2:.3f}".format(**def_metrics))
print("Win-prob Accuracy: {accuracy:.3%}   Brier: {brier:.4f}".format(**win_metrics))

# print(off_m, def_m)
