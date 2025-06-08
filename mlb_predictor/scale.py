import pandas as pd

def fit_standardizer(df, cols):

    params = {}
    for col in cols:
        mean = df[col].mean()
        std = df[col].std()
        params[col] = (mean, std)
    return params

def standardize(df, params):
    standardized_df = df.copy()
    for col, (mean, std) in params.items():
        standardized_df[col] = (df[col] - mean) / std
    return standardized_df

# cols = ['avg', 'obp', 'slg', 'woba', 'wrc_plus', 'war', 'k_pct', 'bb_pct', 'k_per_9', 'bb_per_9', 'hr_per_9', 'era', 'fip', 'owar']
# # Read the data
# data = pd.read_csv("STATSFR.csv")
# # data has exactly two rows per game (home, away)
# data = (
#     data
#     .assign(
#         runs_allowed =                    # new column
#         data.groupby(["game_id", "game_date"])["runs_scored"]
#             .transform(lambda s: s.iloc[::-1].values)    # swap the two rows
#     )
# )


# print(data)

# # Uncomment if you want to standardize the data
# # params = fit_standardizer(data, cols)
# # standardized_data = standardize(data, params)