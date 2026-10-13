import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


df1 = pd.read_csv("races.csv", usecols=["raceId", "year", "round", "circuitId", "date"] , na_values=[r"\N"])
df2 = pd.read_csv("results.csv", usecols=["raceId", "driverId", "constructorId", "grid", "positionOrder"], na_values=[r"\N"])
df3 = pd.read_csv("qualifying.csv", usecols=['raceId', "driverId", "position", "q1", "q2", "q3"] , na_values=[r"\N"])

df3.rename(columns={"position" : "quali_position"} , inplace=True)

partial = pd.merge(df2,df1,on=['raceId'], how="left")
Data = pd.merge(partial,df3,on=['raceId','driverId'] , how="left") 

print(df2.shape[0],partial.shape[0],Data.shape[0])

max_year = Data["year"].max()
min_year = Data["year"].min()

nan_values = Data[Data["year"] >= 2014].isna().sum()

grid_zeros = (Data[Data["year"] >= 2014]["grid"] == 0).sum()


print(max_year,min_year)
print(nan_values)
print(grid_zeros)
print(Data[Data["year"] >= 2014].shape[0])


Data["date"] = pd.to_datetime(Data["date"])

Data["q1_SEC"] = (Data["q1"]).str.split(":")
Data["q1_SEC"] = pd.to_numeric(Data["q1_SEC"].str[0] ) * 60 + pd.to_numeric(Data["q1_SEC"].str[1])

Data["q2_SEC"] = (Data["q2"]).str.split(":")
Data["q2_SEC"] = pd.to_numeric(Data["q2_SEC"].str[0]) * 60 + pd.to_numeric(Data["q2_SEC"].str[1])

Data["q3_SEC"] = (Data["q3"]).str.split(":")
Data["q3_SEC"] = pd.to_numeric(Data["q3_SEC"].str[0] ) * 60 + pd.to_numeric(Data["q3_SEC"].str[1])

Data = Data.sort_values(by="date")
Data.to_csv('2014Onwards.csv',index=False)

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

print(Data[Data["year"] >= 2014].shape[0])
print(list(Data))
