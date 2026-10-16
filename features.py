import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def features():

    df1 = pd.read_csv("races.csv", usecols=["raceId", "year", "round", "circuitId", "date"] , na_values=[r"\N"])
    df2 = pd.read_csv("results.csv", usecols=["raceId", "driverId", "constructorId", "grid", "positionOrder","positionText","laps"], na_values=[r"\N"])
    df3 = pd.read_csv("qualifying.csv", usecols=['raceId', "driverId", "position", "q1", "q2", "q3"] , na_values=[r"\N"])

    df3.rename(columns={"position" : "quali_position"} , inplace=True)

    partial = pd.merge(df2,df1,on=['raceId'], how="left")
    Data = pd.merge(partial,df3,on=['raceId','driverId'] , how="left") 

    # print(df2.shape[0],partial.shape[0],Data.shape[0])

    # max_year = Data["year"].max()
    # min_year = Data["year"].min()

    # nan_values = Data[Data["year"] >= 2014].isna().sum()




    # print(max_year,min_year)
    # print(nan_values)

    # print(Data[Data["year"] >= 2014].shape[0])


    Data["date"] = pd.to_datetime(Data["date"])

    Data["q1"] = (Data["q1"]).str.split(":")
    Data["q1"] = pd.to_numeric(Data["q1"].str[0] ) * 60 + pd.to_numeric(Data["q1"].str[1])

    Data["q2"] = (Data["q2"]).str.split(":")
    Data["q2"] = pd.to_numeric(Data["q2"].str[0]) * 60 + pd.to_numeric(Data["q2"].str[1])

    Data["q3"] = (Data["q3"]).str.split(":")
    Data["q3"] = pd.to_numeric(Data["q3"].str[0] ) * 60 + pd.to_numeric(Data["q3"].str[1])

    Data = Data[~Data['positionText'].isin(['D','W', 'E', 'N'])]


    Data = Data.sort_values(by="date")



    Data["prev_position"] = Data.groupby("driverId")["positionOrder"].shift(1)

    Data["avg_pos_prev_5"] = (
        Data.groupby("driverId")["prev_position"]
        .rolling(window=5, min_periods=5)
        .mean()
        .reset_index(level=0, drop=True)
    )


    team_race_avg = Data.groupby(["constructorId", "raceId" , 'date'])["positionOrder"].mean().reset_index()
    team_race_avg.rename(columns={"positionOrder": "Avg_Position"}, inplace=True)

    team_race_avg = team_race_avg.sort_values(by=['date'])

    team_race_avg["teamRolling"] = (
        team_race_avg.groupby("constructorId")["Avg_Position"]
        .shift(1)
        .groupby(team_race_avg["constructorId"])
        .rolling(window=5, min_periods=5)
        .mean()
        .reset_index(level=0, drop=True)
    )

    Data = pd.merge(Data, team_race_avg[['raceId', 'constructorId', 'teamRolling']], on=['raceId', 'constructorId'], how="left")

    # print(Data.shape[0])
    # print(Data[Data["year"] >= 2014].shape[0])
    # print(list(Data))

    Data = Data[Data["year"] >= 2014]
    # print(Data["positionText"].value_counts())


    # suspect_mask = (Data["grid"] == 0) | (Data["grid"] == "") | (Data["grid"].isna())

    # missing_w_count = Data[ suspect_mask & (Data["positionText"] == "W")].shape[0]
    # print(missing_w_count)

    # grid_zeros = (Data["grid"] == 0).sum()
    # print(grid_zeros)

    # grid_blanks = (Data["grid"].isna()).sum()
    # print(grid_blanks)

    # print(Data[Data['grid'] == 0]['positionText'].value_counts())
    # print(Data[Data['grid'].isna()]['positionText'].value_counts())

    # print(Data[Data['grid'].isna()].groupby('raceId').size().reset_index(name='blank_grid_rows').merge(Data[['raceId', 'year', 'round']], on='raceId').drop_duplicates())

    # print(Data[(Data["raceId"] ==  1183)  | (Data["raceId"] ==  1167 ) ]["quali_position"])

    # print(Data[Data['grid'] == Data["quali_position"]].shape[0])

    # print(Data[(Data['grid'].notna()) & (Data['quali_position'].notna()) & (Data['grid'] > 0)].shape[0])

    # print( Data[ (Data['laps'] == 0) & (Data["positionText"] == "W")].shape[0])
    # print( Data[ (Data['laps'] == 0) & (Data["positionText"] == "R")].shape[0])

    # Data.to_csv('final.csv',index=False)


    Data["pit_lane_start"] = (Data["grid"] == 0).astype(int)

    race_max = (
        Data["grid"].where(Data["grid"] > 0)
        .groupby(Data["raceId"])
        .transform("max")
    )
    pit = Data["grid"] == 0
    Data.loc[pit, "grid"] = race_max[pit] + 1

    q_columns = ['q1', 'q2', 'q3']
    Data["qualified"] = Data[q_columns].notna().sum(axis=1)

    Data["gapQ1"] = ((Data["q1"] - Data.groupby("raceId")["q1"].transform("min")) * 100) / Data.groupby("raceId")["q1"].transform("min")

    Data["gapQ2"] = ((Data["q2"] - Data.groupby("raceId")["q2"].transform("min")) * 100) / Data.groupby("raceId")["q2"].transform("min")

    Data["gapQ3"] = ((Data["q3"] - Data.groupby("raceId")["q3"].transform("min")) * 100) / Data.groupby("raceId")["q3"].transform("min")


    # print(Data.shape[0])
    # print(Data[ Data['laps'] == 0 ].shape[0])

    Data = Data[~Data['raceId'].isin([1167,1183])]

    pairs = pd.merge(Data, Data, on="raceId", suffixes=("_left", "_right"))

    pairs = pairs[~ (pairs["driverId_left"] >= pairs["driverId_right"] )]
    print(pairs.shape)




    pairs = pairs[~((pairs["positionText_left"] == "R" ) & (pairs["positionText_right"] == "R"))]

    X = pd.DataFrame(
        {
            "grid_difference": pairs["grid_left"] - pairs["grid_right"],
            "pit_lane_flag_difference": pairs["pit_lane_start_left"] - pairs["pit_lane_start_right"],
            "quali_position_difference": pairs["quali_position_left"] - pairs["quali_position_right"],
            "qualified_difference": pairs["qualified_left"] - pairs["qualified_right"],
            "gapQ1_difference": pairs["gapQ1_left"] - pairs["gapQ1_right"],
            "gapQ2_difference": pairs["gapQ2_left"] - pairs["gapQ2_right"],
            "gapQ3_difference": pairs["gapQ3_left"] - pairs["gapQ3_right"],
            "driver_form_difference": pairs["avg_pos_prev_5_left"] - pairs["avg_pos_prev_5_right"],
            "team_form_difference": pairs["teamRolling_left"] - pairs["teamRolling_right"],
            "best_grid_slot": pairs[["grid_left", "grid_right"]].min(axis=1)
        }
    )


    np.random.seed(42)  
    flip_flags = np.random.rand(len(X)) > 0.5


    diff_cols = [col for col in X.columns if col.endswith("_difference")]

    X.loc[flip_flags, diff_cols] *= -1

    train_mask = pairs["year_left"].between(2014, 2024)
    test_mask = pairs["year_left"] == 2025

    X_train = X[train_mask].reset_index(drop=True)
    X_test = X[test_mask].reset_index(drop=True)

    missing_columns = X_train.columns[X_train.isna().any()].tolist()
    train_medians = X_train.median().fillna(0.0)

    for column in missing_columns:
        X_train[f"{column}_missing"] = X_train[column].isna().astype(int)
        X_test[f"{column}_missing"] = X_test[column].isna().astype(int)

    X_train = X_train.fillna(train_medians)
    X_test = X_test.fillna(train_medians)


    y = (pairs["positionOrder_left"] < pairs["positionOrder_right"]).astype(int)

    y.loc[flip_flags] = 1 - y.loc[flip_flags]

    y_train = y[train_mask].reset_index(drop=True)
    y_test = y[test_mask].reset_index(drop=True)

    return X_train,X_test,y_train,y_test
