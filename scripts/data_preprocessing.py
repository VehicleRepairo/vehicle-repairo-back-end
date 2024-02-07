#Importing necessary libraries and dependencies
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
import numpy as np

#Setting up dataset path
dataset_path = "../data/vehicle_maintenance_dataset.csv"
#Reading the dataset file and storing it in a pandas data frame variable
df = pd.read_csv(dataset_path)

#Finding out unique values in brand, model and engine type
#print(df["brand"].unique())
#print(df["model"].unique())
#print(df["engine_type"].unique())

#Object containing one-hot encoder
ohe = OneHotEncoder()

#Storing one-hot encoded categorical values
category_features = ohe.fit_transform(df[["brand", "model", "engine_type"]]).toarray()

#Combining converted arrays of one-hot encoded values to one
np.array(category_features).ravel()

#Storing the one-hot coded changes in the dataframe
pd.DataFrame(category_features)

#Storing service types in a variable
service_types = ['oil_filter', 'engine_oil', 'washer_plug_drain', 'dust_and_pollen_filter', 'wheel_alignment_and_balancing'
                ,'air_clean_filter', 'fuel_filter', 'spark_plug', 'brake_fluid', 'brake_and_clutch_oil', 'transmission_fluid',
                'brake_pads', 'clutch', 'coolant']

#Converting service types from int to bool
df[service_types] = df[service_types].astype(bool)

#Previewing pre-processed data
#print(df.columns)
print(df.head())
#print(df.info())
#print(df.describe()) 