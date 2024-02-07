#Importing necessary libraries and dependencies
from sklearn import linear_model
import pandas as pd

#Setting up dataset path
dataset_path = "../data/vehicle_maintenance_dataset.csv"
#Reading the dataset file and storing it in a pandas data frame variable
df = pd.read_csv(dataset_path)

#One-Hot Encoding the categorical columns
df = pd.get_dummies(df, columns=['brand', 'model', 'engine_type'], prefix=None)

#Storing service types in a variable
service_types = ['oil_filter', 'engine_oil', 'washer_plug_drain', 'dust_and_pollen_filter', 'wheel_alignment_and_balancing'
                ,'air_clean_filter', 'fuel_filter', 'spark_plug', 'brake_fluid', 'brake_and_clutch_oil', 'transmission_fluid',
                'brake_pads', 'clutch', 'coolant']

#Converting service types from int to bool
df[service_types] = df[service_types].astype(bool)

#Previewing pre-processed data
#print(df.columns)
#print(df.head())
#print(df.info())
#print(df.describe())