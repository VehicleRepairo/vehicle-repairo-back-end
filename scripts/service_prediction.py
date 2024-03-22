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

def make_predictions(user_input, models):
    user_df = pd.DataFrame([user_input])
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

if __name__ == "__main__":
    service_types = ['washer_plug_drain', 'dust_and_pollen_filter',
                     'wheel_alignment_and_balancing', 'air_clean_filter', 'fuel_filter', 'spark_plug',
                     'brake_fluid', 'brake_and_clutch_oil', 'transmission_fluid', 'brake_pads',
                     'clutch', 'coolant']
    
    models = load_models(service_types)
    
    user_firebase_uid = "jBq6d3yiwmgn1lOwATxRVjWNvp13"

    vehicle_info = get_vehicle_info(user_firebase_uid)

    if vehicle_info:
        vehicle_type = vehicle_info.get('vehicle_type', '').strip().lower()
        brand = vehicle_info.get('Brand', '').strip().lower() 
        model = vehicle_info.get('Model', '').strip().lower()
        engine_type = vehicle_info.get('Engine_type', '').strip().lower()
        mileage = int(vehicle_info.get('mileage', 0))

        print("User data:")
        for key, value in vehicle_info.items():
            print(f"{key}: {value}")

        if vehicle_type != "car":
            print("Feature not available")
        elif brand not in ["honda", "toyota"]:
            print("Feature not available")
        elif brand == "honda" and model not in ["amaze", "jazz", "city"]:
            print("Feature not available")
        elif brand == "toyota" and model != "fortuner":
            print("Feature not available")
        elif engine_type == "petrol" and model != "fortuner":
            if mileage < 5000 or mileage > 104999:
                print("Feature not available")
            else:
                user_input = {
                    'brand_honda': 1 if brand == 'honda' else 0,
                    'brand_toyota': 1 if brand == 'toyota' else 0,
                    'model_amaze': 1 if model == 'amaze' else 0,
                    'model_city': 1 if model == 'city' else 0,
                    'model_fortuner': 1 if model == 'fortuner' else 0,
                    'model_jazz': 1 if model == 'jazz' else 0,
                    'engine_type_diesel': 1 if engine_type == 'diesel' else 0,
                    'engine_type_petrol': 1 if engine_type == 'petrol' else 0,
                    'mileage': mileage,
                    'nearest_thousandth_mileage': ((mileage + 999) // 1000) * 1000
                }
                predictions = make_predictions(user_input, models)
                
                for service_type, prediction in predictions.items():
                    print(f"{service_type}: {prediction}")
        elif engine_type == "diesel" and model == "fortuner":
            if mileage < 5000 or mileage > 104999:
                print("Feature not available")
            else:
                user_input = {
                    'brand_honda': 0,
                    'brand_toyota': 1,
                    'model_amaze': 0,
                    'model_city': 0,
                    'model_fortuner': 1,
                    'model_jazz': 0,
                    'engine_type_diesel': 1,
                    'engine_type_petrol': 0,
                    'mileage': mileage,
                    'nearest_thousandth_mileage': ((mileage + 999) // 1000) * 1000
                }
                predictions = make_predictions(user_input, models)
                
                for service_type, prediction in predictions.items():
                    print(f"{service_type}: {prediction}")
        else:
            print("Feature not available")
    else:
        print("Error: No vehicle information found for the user.")