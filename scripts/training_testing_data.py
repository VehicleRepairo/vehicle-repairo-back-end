#Importing necessary libraries and dependencies
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pandas as pd

#Setting up pre-processed dataset path
dataset_path = "../data/preprocessed_vehicle_maintenance_dataset.csv"

#Storing pre-processed data in a data frame
df = pd.read_csv(dataset_path)

#Initiating features X of the model
X = df[['brand_honda', 'brand_toyota', 'model_amaze', 'model_city', 'model_fortuner'
        , 'model_jazz', 'engine_type_diesel', 'engine_type_petrol', 'mileage', 'nearest_thousandth_mileage']]

#Initiating target variables Y of the model
Y = df[['oil_filter', 'engine_oil', 'washer_plug_drain', 'dust_and_pollen_filter'
        , 'wheel_alignment_and_balancing', 'air_clean_filter', 'fuel_filter', 'spark_plug' 
        , 'brake_fluid', 'brake_and_clutch_oil', 'transmission_fluid', 'brake_pads'
        , 'clutch', 'coolant']]