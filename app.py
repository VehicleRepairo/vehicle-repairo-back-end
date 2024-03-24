from flask import Flask, jsonify, request
from mongoengine import connect
from pymongo import MongoClient
import os
from models.entities.vehicle import Vehicle
from geopy.geocoders import Nominatim
import firebase_admin
from firebase_admin import credentials, firestore
from flask_cors import CORS
from flask_restful import Resource,Api
from bson import ObjectId
from rake_nltk import Rake
import nltk
from api.Guidance import find_word_in_table
import json
from datetime import datetime
from api.ratings_and_reviews import calculate_average_rating, get_reviews
import joblib
import pandas as pd


app = Flask(__name__)
CORS(app) 
api = Api(app)

#mongodb connection
client = MongoClient(f"mongodb+srv://senadi20220678:%23abc%40123@vehicle-repairo.dlhnhh6.mongodb.net/")
db = client['Vehicle_Repairo']
mechanics_collection = db['mechanic']
vehicle_collection = db['vehicle']
appointments_collection = db['appointment']
ratings_collection = db['ratings']
users_collection = db['users']

mechanics_collection.create_index([("coordinates1", "2dsphere")])
appointments_collection.create_index({ "Mech_uid": 1 })

mechanic_average_rating = db['mechanic_average_rating']
connect(host=f"mongodb+srv://senadi20220678:%23abc%40123@vehicle-repairo.dlhnhh6.mongodb.net/")



#firebase connection
cred = credentials.Certificate("./vehicle-repairo-firebase-adminsdk-cmk26-3ac0077dd7.json")
firebase_admin.initialize_app(cred)

class AppointmentResource(Resource):

    def get(self, appointment_id):
        appointment = appointments_collection.find_one({'_id': ObjectId(appointment_id)})
        if appointment:
            return json.loads(json.dumps(appointment, default=str)), 200
        else:
            return {'message': 'Appointment not found'}, 404

    def post(self):
        data = request.get_json()
        appointment_id = appointments_collection.insert_one(data).inserted_id
        return {'appointment_id': str(appointment_id)}, 201

#getting the nearest mechanics and their information from firebase
@app.route('/nearest_mechanics', methods=['POST'])
def get_nearest_mechanics():
    try:
        # Parse request data
        data = request.json
        selected_value = data.get('selectedValue')
        user_longitude = data.get('location', {}).get('longitude')
        user_latitude = data.get('location', {}).get('latitude')
        print(user_latitude, user_longitude)

        # Check if user longitude and latitude are provided
        if not (user_longitude and user_latitude):
            return jsonify({"error": "User location is required"}), 400

        # Construct the MongoDB query to find all mechanics near the user's location
        query = {
            "coordinates1": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [user_longitude, user_latitude]
                    },
                    "$maxDistance": 30000  # 30 kilometers in meters
                }
            }
        }

        # Execute the query to find all mechanics near the user's location
        nearest_mechanics = mechanics_collection.find(query)
        

        # Convert ObjectId to string representation in each document
        mechanics_list = []
        for mechanic in nearest_mechanics:
            mechanic['_id'] = str(mechanic['_id'])  # Convert ObjectId to string
            
            # Fetch additional mechanic details from Firestore
            firestore_details = get_firestore_mechanic_details(mechanic['firebase_uid'])
            
            # Check if the mechanic's category matches the selected value (case-insensitive comparison)
            if selected_value.lower() == firestore_details.get('catergory', '').lower():
                # Calculate average rating for this mechanic
                mechanic_average_rating = calculate_average_rating(mechanic['mechanic_id'])
            
                # Combine data from MongoDB, Firestore, and calculated average rating into a single response
                combined_data = {
                    'name': firestore_details.get('fullName', 'N/A'),
                    'contact': firestore_details.get('contact', 'N/A'),
                    'profilepicurl': firestore_details.get('profilePicURL', 'N/A'),
                    'category': firestore_details.get('catergory', 'N/A'),
                    'location': mechanic.get('Area', 'N/A'),
                    'address': mechanic.get('Address', 'N/A'),
                    'uid': mechanic.get('firebase_uid', 'N/A'),
                    'mech_id': mechanic.get('mechanic_id', 'N/A'),
                    'average_rating': str(mechanic_average_rating)
                }
            
                mechanics_list.append(combined_data)

        # Return the list of mechanics with combined data as JSON response in an array
        return jsonify(mechanics_list)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



def get_firestore_mechanic_details(firebase_uid):
    try:
        # Access Firestore client
        db = firestore.client()

        # Reference to the document with the given Firebase UID in the 'users' collection
        doc_ref = db.collection('users').document(firebase_uid)

        # Get the document snapshot
        doc = doc_ref.get()

        # Check if document exists
        if doc.exists:
            # Get data from document
            mechanic_data = doc.to_dict()
            return mechanic_data

    except Exception as e:
        print(f"Error retrieving mechanic details from Firestore: {e}")

    return {}  # Return an empty dictionary if mechanic details not found or error occurred


#creating a vehicle
@app.route('/vehicle', methods=['POST'])
def create_vehicle():
    # Extract data from the request
    data = request.json

    # Create a new vehicle document
    new_vehicle = Vehicle(
        vehicle_type=data.get('vehicle_type'),
        Brand=data.get('Brand'),
        Model=data.get('Model'),
        Engine_type=data.get('Engine_type'),
        mileage=data.get('mileage'),
        firebase_uid=data.get('firebase_uid')
    )

    # Convert the new_vehicle object into a dictionary
    vehicle_data = {
        'vehicle_type': new_vehicle.vehicle_type,
        'Brand': new_vehicle.Brand,
        'Model': new_vehicle.Model,
        'Engine_type': new_vehicle.Engine_type,
        'mileage': new_vehicle.mileage,
        'firebase_uid': new_vehicle.firebase_uid
    }

    # Insert the vehicle data into the vehicle collection
    db.vehicle.insert_one(vehicle_data)

    return jsonify({"message": "Vehicle created successfully"}), 201

service_types = ['washer_plug_drain', 'dust_and_pollen_filter',
                'wheel_alignment_and_balancing', 'air_clean_filter', 'fuel_filter', 'spark_plug',
                'brake_fluid', 'brake_and_clutch_oil', 'transmission_fluid', 'brake_pads',
                'clutch', 'coolant']

def load_models(service_types):
    loaded_models = {}
    models_path = "models"
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
        if prediction[0]:  # Check if the prediction is True
            predictions[service_type] = bool(prediction[0])
    return predictions

def get_vehicle_info(user_firebase_uid):
    vehicle_info = vehicle_collection.find_one({"firebase_uid": user_firebase_uid})
    return vehicle_info

def preprocess_vehicle_info(vehicle_info):
    if not vehicle_info:
        return None
    
    vehicle_info = {key: value.strip() if isinstance(value, str) else value for key, value in vehicle_info.items()}
    vehicle_info['Brand'] = vehicle_info['Brand'].lower().strip()
    vehicle_info['Model'] = vehicle_info['Model'].lower().strip()
    vehicle_info['Engine_type'] = vehicle_info['Engine_type'].lower().strip()
    
    return vehicle_info

def get_one_hot_encoded_features(vehicle_info):
    one_hot_encoded = {
        'brand_honda': 1 if vehicle_info['Brand'] == 'honda' else 0,
        'brand_toyota': 1 if vehicle_info['Brand'] == 'toyota' else 0,
        'model_amaze': 1 if vehicle_info['Model'] == 'amaze' else 0,
        'model_city': 1 if vehicle_info['Model'] == 'city' else 0,
        'model_fortuner': 1 if vehicle_info['Model'] == 'fortuner' else 0,
        'model_jazz': 1 if vehicle_info['Model'] == 'jazz' else 0,
        'engine_type_diesel': 1 if vehicle_info['Engine_type'] == 'diesel' else 0,
        'engine_type_petrol': 1 if vehicle_info['Engine_type'] == 'petrol' else 0,
    }
    return one_hot_encoded

def get_nearest_mileage(mileage):
    return ((mileage + 999) // 1000) * 1000

@app.route('/predict_service/<string:firebase_uid>', methods=['POST'])
def predict_service(firebase_uid):
    user_firebase_uid = firebase_uid
    
    vehicle_info = get_vehicle_info(user_firebase_uid)
    vehicle_info = preprocess_vehicle_info(vehicle_info)

    if not vehicle_info:
        return jsonify({'error': 'No vehicle information found for the user'}), 200

    mileage = int(vehicle_info.get('mileage', 0))
    if mileage < 5000 or mileage > 104999:
        return jsonify({'error': 'Cannot predict for mileage less than 5000 or above 105000'}), 200

    vehicle_type = vehicle_info.get('vehicle_type', '').strip().lower()
    if vehicle_type != "car":
        return jsonify({'error': 'Feature not available for non-car vehicles'}), 200

    brand = vehicle_info.get('Brand', '').strip().lower()
    if brand not in ["honda", "toyota"]:
        return jsonify({'error': 'Feature not available for non-Honda/Toyota vehicles'}), 200

    if brand == "honda":
        model = vehicle_info.get('Model', '').strip().lower()
        if model not in ["amaze", "city", "jazz"]:
            return jsonify({'error': 'Feature not available for this Honda model'}), 200
    elif brand == "toyota":
        model = vehicle_info.get('Model', '').strip().lower()
        if model != "fortuner":
            return jsonify({'error': 'Feature not available for this Toyota model'}), 200

    engine_type = vehicle_info.get('Engine_type', '').strip().lower()
    if brand == "honda" and engine_type != "petrol" and engine_type != "diesel":
        return jsonify({'error': 'Feature not available for Honda models with engine type other than petrol and diesel'}), 200

    if brand == "toyota" and model == "fortuner" and engine_type != "diesel":
        return jsonify({'error': 'Feature not available for Toyota Fortuner with engine type other than diesel'}), 200

    one_hot_encoded = get_one_hot_encoded_features(vehicle_info)

    nearest_mileage = get_nearest_mileage(mileage)
    user_input = {**one_hot_encoded, 'mileage': mileage, 'nearest_thousandth_mileage': nearest_mileage}

    models = load_models(service_types)
    predictions = make_predictions(user_input, models)

    return jsonify(predictions)



#change mileage
@app.route('/vehicle/<firebase_uid>', methods=['PATCH'])
def update_vehicle(firebase_uid):
    # Extract data from the request
    data = request.json

    # Retrieve the vehicle document by firebase_UID
    vehicle = vehicle_collection.find_one({"firebase_uid": firebase_uid})

    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404

    # Retrieve the current mileage and add the new mileage
    current_mileage = vehicle.get('mileage', 0)
    new_mileage = data.get('mileage')

    if new_mileage is None:
        return jsonify({"error": "New mileage value is missing"}), 400

    total_mileage = current_mileage + new_mileage

    # Update the vehicle document with the new total mileage
    vehicle_collection.update_one({"_id": ObjectId(vehicle['_id'])}, {"$set": {"mileage": total_mileage}})

    return jsonify({"message": f"Mileage updated successfully. New total mileage: {total_mileage}"}), 200



#update total mileage
@app.route('/mileage/<firebase_uid>', methods=['PATCH'])
def update_mileage(firebase_uid):
    # Extract data from the request
    data = request.json

    # Retrieve the vehicle document by firebase_UID
    vehicle = vehicle_collection.find_one({"firebase_uid": firebase_uid})

    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404

    # Update the vehicle document with the new total mileage
    vehicle_collection.update_one({"_id": ObjectId(vehicle['_id'])}, {"$set": {"mileage": data.get('mileage')}})

    return jsonify({"message": f"Mileage updated successfully. Total mileage: {data.get('mileage')}"}), 200



# Global variable to store the mechanic_id counter
mechanic_id_counter = None

def get_mechanic_id_counter():
    global mechanic_id_counter
    if mechanic_id_counter is None:
        # Fetch the counter from the database
        counter_doc = mechanics_collection.find_one({'_id2': 'mechanic_id_counter'})
        if counter_doc:
            mechanic_id_counter = counter_doc['value']
        else:
            # Initialize the counter if it doesn't exist
            mechanic_id_counter = 0
            mechanics_collection.insert_one({'_id2': 'mechanic_id_counter', 'value': mechanic_id_counter})
    return mechanic_id_counter

def increment_mechanic_id_counter():
    global mechanic_id_counter
    mechanic_id_counter += 1
    mechanics_collection.update_one({'_id2': 'mechanic_id_counter'}, {'$set': {'value': mechanic_id_counter}})

@app.route('/profile', methods=['POST'])
def convert_address_to_coordinates():
    global mechanic_id_counter  # Access the global variable

    # Extract data from the request
    data = request.json
    address = data.get('address')
    location = data.get('location')
    firebase_uid = data.get('firebase_uid')

    # Use geopy to convert address to coordinates
    geolocator = Nominatim(user_agent="GetLoc")
    geo_location = geolocator.geocode(address) if address else None

    if geo_location:
        latitude = geo_location.latitude
        longitude = geo_location.longitude

        # Get the next mechanic ID
        mechanic_id_counter = get_mechanic_id_counter()
        mechanic_id_counter += 1
        mechanic_id = f"mech_{mechanic_id_counter}"
        
        # Increment the mechanic ID counter
        increment_mechanic_id_counter()

        # Check if firebase_uid exists
        existing_mechanic = mechanics_collection.find_one({'firebase_uid': firebase_uid})

        update_data = {
            'mechanic_id': mechanic_id,
            'coordinates1': {
                'type': 'Point',
                'coordinates': [longitude, latitude]
            },
            'firebase_uid': firebase_uid,
            'Area': address,
            'Address': location
        }

        if existing_mechanic:
            # Update existing mechanic document
            update_data['mechanic_id'] = existing_mechanic['mechanic_id']  # Preserve existing mechanic_id
            mechanics_collection.update_one(
                {'firebase_uid': firebase_uid},
                {'$set': update_data}
            )
            return jsonify({"message": "Mechanic location updated successfully"}), 200
        else:
            # Insert new mechanic document with mechanic_id
            mechanics_collection.insert_one(update_data)
            return jsonify({"message": "New mechanic added successfully"}), 201
    else:
        return jsonify({"error": "Failed to convert address to coordinates or address is not provided"}), 400



#getting mechanic location and id to update mechanic profile
@app.route('/location', methods=['POST'])
def get_location():
    data = request.json
    uid = data.get('uid')
    
    existing_mechanic = mechanics_collection.find_one({'firebase_uid': uid})
    
    if existing_mechanic:
        city = existing_mechanic.get('Area', '')
        location = existing_mechanic.get('Address', '')
        mech_id = existing_mechanic.get('mechanic_id')
        mechanic_average_rating = calculate_average_rating(mech_id)
        
        return jsonify({"city": city, "address": location, "mechanic_id":mech_id, "rating": mechanic_average_rating}), 200
       
    else:
        return jsonify({"message": "Enter your location"}), 404



#create appointment 
@app.route('/create_appointment', methods=['POST'])
def create_appointment():
    data = request.json
    user_uid = data.get('user_uid')
    print(user_uid)

    appointment_data = {
        'Appointments_time': data.get('Appointments_time'),
        'Date_of_appointment': data.get('Date_of_appointment'),
        'Name':data.get('Name'),
        'user_uid': user_uid,
        'contact': data.get('contact'),
        'Service_Required': data.get('Service_Required'),
        'vehicle':data.get('vehicle') ,
        'Mech_uid': data.get('Mech_uid'),

    }

    appointment_id = db.appointment.insert_one(appointment_data).inserted_id

    return jsonify({'success': True, 'appointment_id': str(appointment_id)})


#getting related mechanics appointments
@app.route('/appointments/<mechanic_uid>', methods=['GET'])
def get_appointments_by_mechanic_uid(mechanic_uid):
    appointments = appointments_collection.find({'Mech_uid': mechanic_uid})
    appointments_list = list(appointments)
    for appointment in appointments_list:
        appointment['_id'] = str(appointment['_id'])

    return jsonify(appointments_list)



#delete
@app.route('/appointments/<string:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    try:
        # Find the appointment to be deleted
        appointment = appointments_collection.find_one({'_id': ObjectId(appointment_id)})
        if not appointment:
            return jsonify({'message': 'Appointment not found'}), 404

        # Insert user data into the users collection
        user_data = {
            'user_uid': appointment.get('user_uid'),
            'appointment_status': 'Appointment was declined'
        }
        users_collection.insert_one(user_data)

        # Delete the appointment from the appointments collection
        result = appointments_collection.delete_one({'_id': ObjectId(appointment_id)})
        if result.deleted_count == 1:
            return jsonify({'message': 'Appointment deleted successfully'}), 200
        else:
            return jsonify({'message': 'Appointment not found'}), 404
    except Exception as e:
        print("Error:", e)
        return jsonify({'message': 'Internal server error'}),500
    

#done
@app.route('/done/<string:appointment_id>', methods=['DELETE'])
def done_appointment(appointment_id):
    try:
        # Find the appointment to be deleted
        appointment = appointments_collection.find_one({'_id': ObjectId(appointment_id)})
        if not appointment:
            return jsonify({'message': 'Appointment not found'}), 404

        # Insert user data into the users collection
        user_data = {
            'user_uid': appointment.get('user_uid'),
            'appointment_status': 'Appointment is done'
        }
        users_collection.insert_one(user_data)

        # Delete the appointment from the appointments collection
        result = appointments_collection.delete_one({'_id': ObjectId(appointment_id)})
        if result.deleted_count == 1:
            return jsonify({'message': 'Appointment completed successfully'}), 200
        else:
            return jsonify({'message': 'Appointment not found'}), 404
    except Exception as e:
        print("Error:", e)
        return jsonify({'message': 'Internal server error'}),500



# Getting ratings for a specific mechanic ID
@app.route('/ratings/<string:mech_id>', methods=['GET'])
def get_ratings(mech_id):
    try:
        results = ratings_collection.find({"mechanic_id": mech_id})
        ratings = []
        for result in results:
            # Extract the rating details from each result
            rating = {
                "mechanic_id": result["mechanic_id"],
                "rating": result["rating"],
                "comment": result["comment"],
                "timestamp": result["timestamp"]
            }
            ratings.append(rating)
        
        return jsonify(ratings)  # Always return the ratings
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Endpoint to receive ratings and reviews 
@app.route('/submit_review', methods=['POST'])
def submit_review():
    data = request.json
    mechanic_id = data.get('mechanic_id')
    rating = data.get('rating')
    comment = data.get('comment')

    if mechanic_id and rating is not None and isinstance(rating, int) and comment:
        # Add review to the database
        add_review(mechanic_id, rating, comment)
        return jsonify({"message": "Review submitted successfully"}), 200
    else:
        return jsonify({"error": "Invalid data. Please provide mechanic_id, rating (as an integer), and comment"}), 400



# Function to add a new review
def add_review(mechanic_id, rating, comment):
    review = {
        'mechanic_id': mechanic_id,
        'rating': rating,
        'comment': comment,
        'timestamp': datetime.now()
    }
    ratings_collection.insert_one(review)


#guidance
@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    search_query = data.get('searchText', '')

    collection = db["Guidelines"]

    result_rows = find_word_in_table(collection, search_query)

    response = {
        'results': result_rows
    }
    return jsonify(response)


#get users sppointment status
@app.route('/get_appointment_status/<userid>', methods=['GET'])
def get_appointment_status(userid):
    try:
        # Find the user in the users collection based on the user ID
        user = users_collection.find_one({'user_uid': userid})

        if user:
            # Retrieve the appointment status value from the user document
            appointment_status = user.get('appointment_status', 'Appointment status not found')
            return jsonify({'userid': userid, 'appointment_status': appointment_status}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500



#delete appointment status
@app.route('/delete_status/<userid>', methods=['DELETE'])
def delete_appointment_status(userid):
    try:
        # Find the user in the users collection based on the user ID
        user = users_collection.find_one({'user_uid': userid})
        
        if user:
            # If user is found, delete their appointment status
            users_collection.delete_one({'user_uid': userid})
            return "Appointment status deleted successfully.", 200
        else:
            return "User not found.", 404
    except Exception as e:
        return str(e), 500


api.add_resource(AppointmentResource, '/appointment')

if __name__ == '__main__':
    nltk.download("stopwords")
    nltk.download('punkt')
    app.run(host='0.0.0.0', port=8000)
