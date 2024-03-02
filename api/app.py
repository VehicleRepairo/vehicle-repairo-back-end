from flask import Flask, jsonify, request
from mongoengine import connect
from pymongo import MongoClient
import os
from dotenv import load_dotenv,find_dotenv
from Persistance.mechanic import Mechanic
from Persistance.vehicle import Vehicle
from geopy.geocoders import Nominatim
import firebase_admin
from firebase_admin import credentials, firestore
from flask_cors import CORS
from flask_restful import Resource,Api
import json
from bson import ObjectId




load_dotenv(find_dotenv())
password = os.environ.get("MONGODB_PWD")


app = Flask(__name__)
CORS(app) 
api = Api(app)

#mongodb connection
client = MongoClient(f"mongodb+srv://devindhigurusinghe:{password}.@cluster1.k3fvpdq.mongodb.net/")
db = client['test']
mechanics_collection = db['mechanic']
# user_locations_collection = db['user_locations']

connect(host=f"mongodb+srv://devindhigurusinghe:{password}.@cluster1.k3fvpdq.mongodb.net/")
appointments_collection = db['appointments']



#firebase connection
cred = credentials.Certificate("./vehicle-repairo-firebase-adminsdk-cmk26-3ac0077dd7.json")
firebase_admin.initialize_app(cred)

class AllAppointmentsResource(Resource):
    def get(self):
        appointments = appointments_collection.find()
        if appointments:
            return [json.loads(json.dumps(appointment, default=str)) for appointment in appointments], 200
        else:
            return {'message': 'No appointments found'}, 404

api.add_resource(AllAppointmentsResource, '/appointment') 

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

    def put(self, appointment_id):
        data = request.get_json()
        result = appointments_collection.update_one({'_id': ObjectId(appointment_id)}, {'$set': data})
        if result.modified_count > 0:
            return {'message': 'Appointment updated successfully'}, 200
        else:
            return {'message': 'Appointment not found'}, 404
        
    def delete(self, _id):
        result = appointments_collection.delete_one({'_id': ObjectId(_id)})
        if result.deleted_count > 0:
            return {'message': 'Appointment deleted successfully'}, 200
        else:
            return {'message': 'Appointment not found'}, 404


@app.route('/nearest_mechanics', methods=['POST'])
def get_nearest_mechanics():
    try:
        # Parse request data
        data = request.json
        user_longitude = data.get('location', {}).get('longitude')
        user_latitude = data.get('location', {}).get('latitude')
        selected_value = data.get('selectedValue')
        print(user_latitude,user_longitude)
        # Check if user longitude, latitude, and selected value are provided
        if not (user_longitude and user_latitude and selected_value):
            return jsonify({"error": "User location and selected value are required"}), 400

        # Construct the MongoDB query
        query = {
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [user_longitude, user_latitude]
                    },
                    "$maxDistance": 30000  # 30 kilometers in meters
                }
            },
            "category": selected_value
        }

        # Execute the query
        nearest_mechanics = mechanics_collection.find(query)
        print(nearest_mechanics)

        # Iterate through the mechanics and retrieve details from Firestore
        mechanics_details = []
        for mechanic in nearest_mechanics:
            firebase_uid = mechanic.get('firebase_uid')
            if firebase_uid:
                # Get details from Firestore using Firebase UID
                mechanic_details = get_mechanic_details_from_firestore(firebase_uid,selected_value)
                if mechanic_details:
                    mechanics_details.append(mechanic_details)

        if mechanics_details:
            return jsonify(mechanics_details)
        else:
            return jsonify({"message": f"No mechanics found for category '{selected_value}' near your location"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

from firebase_admin import firestore
def get_mechanic_details_from_firestore(firebase_uid, selected_value, mechanics_array):
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

            # Convert both doc_type and selected_value to lowercase for case-insensitive comparison
            doc_type_lowercase = mechanic_data.get('doc_type', '').lower()
            selected_value_lowercase = selected_value.lower()

            # Check if the lowercase document type matches the lowercase selected value
            if doc_type_lowercase == selected_value_lowercase:
                mechanics_array.append(mechanic_data)
        else:
            print(f"No mechanic found with Firebase UID: {firebase_uid}")

    except Exception as e:
        print(f"Error retrieving mechanic details from Firestore: {e}")


@app.route('/mechanics', methods=['POST'])
def create_mechanic():
    # Extract data from the request
    data = request.json

    # Create a new mechanic document
    new_mechanic = Mechanic(
    name=data.get('name'),
    Area=data.get('Area'),
    Contact=data.get('Contact'),
    Type=data.get('Type'),
    Reviews=data.get('Reviews', []),
    location=data.get('location')
)


    # Save the new mechanic document to the database
    new_mechanic.save()
    print(new_mechanic)

    return jsonify({"message": "Mechanic created successfully"}), 201


@app.route('/vehicle', methods=['POST'])
def create_vehicle():
    # Extract data from the request
    data = request.json

    # Create a new mechanic document
    new_vehicle = Vehicle(
    vehicle_type=data.get('vehicle_type'),
    Brand=data.get('Brand'),
    Model=data.get('Model'),
    Engine_type=data.get('Engine_type'),
    mileage =data.get('mileage'),
    firebase_uid = data.get('firebase_uid')
)


    # Save the new mechanic document to the database
    new_vehicle.save()
    print(new_vehicle)

    return jsonify({"message": "vehicle created successfully"}), 201

@app.route('/vehicle/<firebase_uid>', methods=['PATCH'])
def update_vehicle(firebase_uid):
    # Extract data from the request
    data = request.json

    # Retrieve the vehicle document by firebase_UID
    vehicle = Vehicle.objects(firebase_uid=firebase_uid).first()

    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404

    # Retrieve the current mileage and add the new mileage
    current_mileage = vehicle.mileage
    new_mileage = data.get('mileage')

    if new_mileage is None:
        return jsonify({"error": "New mileage value is missing"}), 400

    total_mileage = current_mileage + new_mileage

    # Update the vehicle document with the new total mileage
    vehicle.mileage = total_mileage
    vehicle.save()

    return jsonify({"message": f"Mileage updated successfully. New total mileage: {total_mileage}"}), 200


@app.route('/mileage/<firebase_uid>', methods=['PATCH'])
def update_mileage(firebase_uid):
    # Extract data from the request
    data = request.json

    # Retrieve the vehicle document by firebase_UID
    vehicle = Vehicle.objects(firebase_uid=firebase_uid).first()

    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404

    # Update the vehicle document with the new total mileage
    vehicle.mileage = data.get('mileage')
    vehicle.save()

    return jsonify({"message": f"Mileage updated successfully. Total mileage: {vehicle.mileage}"}), 200

# Convert address to coordinates
@app.route('/profile', methods=['POST'])
def convert_address_to_coordinates():
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

        # Check if firebase_uid exists
        existing_mechanic = mechanics_collection.find_one({'firebase_uid': firebase_uid})

        update_data = {
            'coordinates': {
                'type': 'Point',
                'coordinates': [longitude, latitude]
            },
            'firebase_uid': firebase_uid,
            'Area': address,
            'Address': location
        }

        if existing_mechanic:
            # Update existing mechanic document
            mechanics_collection.update_one(
                {'firebase_uid': firebase_uid},
                {'$set': update_data}
            )
            return jsonify({"message": "Mechanic location updated successfully"}), 200
        else:
            # Insert new mechanic document
            mechanics_collection.insert_one(update_data)
            return jsonify({"message": "New mechanic added successfully"}), 201
    else:
        return jsonify({"error": "Failed to convert address to coordinates"}), 400




@app.route('/location', methods=['POST'])
def get_location():
    data = request.json
    uid = data.get('uid')
    
    existing_mechanic = mechanics_collection.find_one({'firebase_uid': uid})
    
    if existing_mechanic:
        city = existing_mechanic.get('Area', '')
        location = existing_mechanic.get('Address', '')
        return jsonify({"city": city, "address": location}), 200
    else:
        return jsonify({"message": "Enter your location"}), 404




api.add_resource(AppointmentResource, '/appointment')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
