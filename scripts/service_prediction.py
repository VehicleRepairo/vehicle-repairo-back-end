import pandas as pd
import joblib
import os

def load_models(service_types):
    loaded_models = {}
    models_folder = "../models"  # Assuming models folder is located one level up
    for service_type in service_types:
        filename = os.path.join(models_folder, f"{service_type}.pkl")
        loaded_model = joblib.load(filename)
        loaded_models[service_type] = loaded_model
    return loaded_models


def get_user_input():
    print("Please provide the following information for prediction:")
    
    brand = input("Enter the brand (Honda/Toyota): ").lower()
    model = input("Enter the model (Amaze/City/Fortuner/Jazz): ").lower()
    engine_type = input("Enter the engine type (Diesel/Petrol): ").lower()
    
    # Convert user input to one-hot encoded format
    user_input = {
        'brand_honda': 1 if brand == 'honda' else 0,
        'brand_toyota': 1 if brand == 'toyota' else 0,
        'model_amaze': 1 if model == 'amaze' else 0,
        'model_city': 1 if model == 'city' else 0,
        'model_fortuner': 1 if model == 'fortuner' else 0,
        'model_jazz': 1 if model == 'jazz' else 0,
        'engine_type_diesel': 1 if engine_type == 'diesel' else 0,
        'engine_type_petrol': 1 if engine_type == 'petrol' else 0
    }
    
    mileage = int(input("Enter the mileage: "))
    user_input['mileage'] = mileage
    
    # Round up mileage to nearest thousandth
    nearest_thousandth_mileage = ((mileage + 999) // 1000) * 1000
    user_input['nearest_thousandth_mileage'] = nearest_thousandth_mileage
    
    return user_input



def make_predictions(user_input, models):
    user_df = pd.DataFrame([user_input])
    predictions = {}
    for service_type, model in models.items():
        prediction = model.predict(user_df)
        predictions[service_type] = prediction
    return predictions

if __name__ == "__main__":
    # Assuming features and service_types are defined somewhere
    service_types = ['washer_plug_drain', 'dust_and_pollen_filter',
                     'wheel_alignment_and_balancing', 'air_clean_filter', 'fuel_filter', 'spark_plug',
                     'brake_fluid', 'brake_and_clutch_oil', 'transmission_fluid', 'brake_pads',
                     'clutch', 'coolant']
    
    # Load the trained models
    models = load_models(service_types)
    
    # Get user input
    user_input = get_user_input()
    
    # Make predictions
    predictions = make_predictions(user_input, models)
    
    # Print predictions
    for service_type, prediction in predictions.items():
        print(f"{service_type}: {prediction}")