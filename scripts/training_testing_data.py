#Importing necessary libraries and dependencies
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

#Setting up pre-processed dataset path
dataset_path = "../data/preprocessed_vehicle_maintenance_dataset.csv"

#Storing pre-processed data in a data frame
df = pd.read_csv(dataset_path)

#Initiating features X of the model
X = df[['brand_honda', 'brand_toyota', 'model_amaze', 'model_city', 'model_fortuner'
        , 'model_jazz', 'engine_type_diesel', 'engine_type_petrol', 'mileage', 'nearest_thousandth_mileage']]

#Storing all service types in a list
service_types = ['washer_plug_drain', 'dust_and_pollen_filter',
                 'wheel_alignment_and_balancing', 'air_clean_filter', 'fuel_filter', 'spark_plug',
                 'brake_fluid', 'brake_and_clutch_oil', 'transmission_fluid', 'brake_pads',
                 'clutch', 'coolant']

#Splitting dataset for testing and training
X_train, X_test, y_train, y_test = train_test_split(X, df[service_types], test_size=0.2, random_state=42)

#Models dictionary to store each service type regression model 
models = {}

#Loop to run each service type model
for service_type in service_types:
    model = LogisticRegression(max_iter=10000)
    model.fit(X_train, y_train[service_type])
    models[service_type] = model

#Predictions dictionary to store the output of each model and evaluate its metrics
predictions = {}
for service_type in service_types:
    predictions[service_type] = models[service_type].predict(X_test)

#Accuracy dictionary to store the accuracy scores of each model
accuracy_scores = {}

#Loop to calculate accuracy score of each model
for service_type in service_types:
    accuracy = accuracy_score(y_test[service_type], predictions[service_type])
    accuracy_scores[service_type] = accuracy

#print('\nAccuracy for each service type model: \n')

#Loop to print accuracy score of each model
#for service_type, accuracy in accuracy_scores.items():
#    print(f"{service_type}: {accuracy}")

#Precision dictionary to store the precision scores of each model
precision_scores = {}

#Loop to calculate precision score of each model
for service_type in service_types:
    precision = precision_score(y_test[service_type], predictions[service_type])
    precision_scores[service_type] = precision

#print('\nPrecision for each service type model: \n')

#Loop to print precision score of each model
#for service_type, precision in precision_scores.items():
#    print(f"{service_type}: {precision}")

#Recall dictionary to store the recall scores of each model
recall_scores = {}

#Loop to calculate recall score of each model
for service_type in service_types:
    recall = recall_score(y_test[service_type], predictions[service_type])
    recall_scores[service_type] = recall

#print('\nRecall for each service type model: \n')

#Loop to print recall score of each model
#for service_type, recall in recall_scores.items():
#    print(f"{service_type}: {recall}")

#Recall dictionary to store the recall scores of each model
f1_scores = {}

#Loop to calculate recall score of each model
for service_type in service_types:
    f1 = f1_score(y_test[service_type], predictions[service_type])
    f1_scores[service_type] = f1

print('\nF1 for each service type model: \n')

#Loop to print f1 score of each model
for service_type, f1 in f1_scores.items():
    print(f"{service_type}: {f1}")