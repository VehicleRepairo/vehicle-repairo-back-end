#Importing necessary libraries and dependencies
from sklearn import linear_model
import pandas as pd

#Setting up dataset path
dataset_path = "../data/vehicle_maintenance_dataset.csv"
#Reading the dataset file and storing it in a pandas data frame variable
df = pd.read_csv(dataset_path)
print(df.columns)

#One-Hot Encoding the categorical columns
df = pd.get_dummies(df, columns=['brand', 'model', 'engine_type'], prefix=None)