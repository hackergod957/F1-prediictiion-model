import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


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


Data[Data["grid"] == 0 ]["grid"] = Data["grid"].max() + 1

q_columns = ['q1', 'q2', 'q3']
Data["qualified"] = Data[q_columns].notna().sum(axis=1)

Data["gapQ1"] = ((Data["q1"] - Data.groupby("raceId")["q1"].transform("min")) * 100) / Data.groupby("raceId")["q1"].transform("min")

Data["gapQ2"] = ((Data["q2"] - Data.groupby("raceId")["q2"].transform("min")) * 100) / Data.groupby("raceId")["q2"].transform("min")

Data["gapQ3"] = ((Data["q3"] - Data.groupby("raceId")["q3"].transform("min")) * 100) / Data.groupby("raceId")["q3"].transform("min")