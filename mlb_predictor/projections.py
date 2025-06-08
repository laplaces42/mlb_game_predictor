import pandas as pd

def batch_marcel_projections(season_df, stats_to_project, projection_years, reg_constant=3):
    """
    Generate Marcel-style projections for all teams, all stats, for multiple years.

    Parameters:
        season_df (pd.DataFrame): team-season-level stats
        stats_to_project (list[str]): e.g. ["WAR", "wOBA", "FIP"]
        projection_years (list[int]): e.g. [2023, 2024, 2025]
        reg_constant (float): strength of regression to league average

    Returns:
        pd.DataFrame: projected stats for each team and year
    """
    projections = []

    teams = season_df["team"].unique()

    for year in projection_years:
        y1, y2, y3 = year - 1, year - 2, year - 3
        league_stats = season_df[season_df["year"] == y1]

        for team in teams:
            team_stats = season_df[
                (season_df["team"] == team) &
                (season_df["year"].isin([y1, y2, y3]))
            ]

            if len(team_stats) < 3:
                print(f"Skipping {team} for {year}: not enough data")
                continue  # Skip teams with missing history

            team_row = {
                "team": team,
                "year": year
            }

            for stat in stats_to_project:
                try:
                    stat_y1 = team_stats[team_stats["year"] == y1][stat].values[0]
                    stat_y2 = team_stats[team_stats["year"] == y2][stat].values[0]
                    stat_y3 = team_stats[team_stats["year"] == y3][stat].values[0]
                    league_avg = league_stats[stat].mean()

                    weighted_sum = 5 * stat_y1 + 4 * stat_y2 + 3 * stat_y3 + reg_constant * league_avg
                    projected_stat = weighted_sum / (12 + reg_constant)

                    team_row[stat] = projected_stat
                except (IndexError, KeyError):
                    team_row[stat] = None  # Skip if stat missing

            projections.append(team_row)

    return pd.DataFrame(projections)

# stats = ['AVG', 'OBP', 'SLG', 'WRC+', 'WAR', 'K Percentage', 'BB Percentage', 'Opposing K/9', 'Opposing HR/9', 'Opposing BB/9', 'ERA', 'Opposing WAR', 'wOBA', 'FIP']
# years = [2023, 2024, 2025]