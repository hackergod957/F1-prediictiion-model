import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split


df1 = pd.read_csv("races.csv", )
df2 = pd.read_csv("results.csv", usecols=['year','round','circuit'])
df3 = pd.read_csv("qualifying.csv", usecols=['raceId','driverId'])


partial = pd.merge([df1,df2],on=['raceId'])
merged = pd.merge([partial,df3],on=['raceId','driverId'])
merged.to_csv('merged_output.csv', index=False)


Data = pd.read_csv('merged_output.csv')

