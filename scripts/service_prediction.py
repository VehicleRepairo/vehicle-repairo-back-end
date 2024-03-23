import pandas as pd
import joblib
import os
from pymongo import MongoClient

client = MongoClient(f"mongodb+srv://senadi20220678:%23abc%40123@vehicle-repairo.dlhnhh6.mongodb.net/")
db = client['Vehicle_Repairo']
vehicle_collection = db['vehicle']

def load_models(service_types):
    loaded_models = {}
    models_path = "../models"
    for service_type in service_types:
        filename = os.path.join(models_path, f"{service_type}.pkl")
        loaded_model = joblib.load(filename)
        loaded_models[service_type] = loaded_model
    return loaded_models

def make_predictions(user_vehicle_details, models):
    user_df = pd.DataFrame([user_vehicle_details])
    predictions = {}
    for service_type, model in models.items():
        prediction = model.predict(user_df)
        predictions[service_type] = prediction
    return predictions

def get_vehicle_info(user_firebase_uid):
    vehicle_info = vehicle_collection.find_one({"firebase_uid": user_firebase_uid})
    if vehicle_info:
        vehicle_info = {key: value.strip() if isinstance(value, str) else value for key, value in vehicle_info.items()}
        vehicle_info['Brand'] = vehicle_info['Brand'].lower().strip()
        vehicle_info['Model'] = vehicle_info['Model'].lower().strip()
        vehicle_info['Engine_type'] = vehicle_info['Engine_type'].lower().strip()
    return vehicle_info