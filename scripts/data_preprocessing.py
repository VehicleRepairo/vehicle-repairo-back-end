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
#print(category_features)

#Storing one-hot encoded columns into a new dataframe
df_encoded = pd.concat([df, pd.DataFrame(category_features, columns=ohe.get_feature_names_out(["brand", "model", "engine_type"]))], axis=1)

#Dropping the categorical columns from the new dataframe
df_encoded.drop(columns=["brand", "model", "engine_type"], inplace=True)

#Storing service types in a variable
service_types = ['oil_filter', 'engine_oil', 'washer_plug_drain', 'dust_and_pollen_filter', 'wheel_alignment_and_balancing'
                ,'air_clean_filter', 'fuel_filter', 'spark_plug', 'brake_fluid', 'brake_and_clutch_oil', 'transmission_fluid',
                'brake_pads', 'clutch', 'coolant']

#Converting service types from int to bool
df_encoded[service_types] = df[service_types].astype(bool)

#Previewing pre-processed data
#print(df_encoded.columns)
#print(df_encoded.head())
print(df_encoded.info())
#print(df.describe()) 