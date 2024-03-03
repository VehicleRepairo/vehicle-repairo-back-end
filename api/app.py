from flask import Flask, jsonify, request
from mongoengine import connect
from pymongo import MongoClient
import os
from dotenv import load_dotenv,find_dotenv
from models.entities.mechanic import Mechanic
from models.entities.vehicle import Vehicle
from geopy.geocoders import Nominatim
import firebase_admin
from firebase_admin import credentials, firestore
from flask_cors import CORS
from flask_restful import Resource,Api
from bson import ObjectId
import json

load_dotenv(find_dotenv())
password = os.environ.get("MONGODB_PWD")


app = Flask(__name__)
CORS(app) 
api = Api(app)

#mongodb connection
client = MongoClient(f"mongodb+srv://devindhigurusinghe:{password}.@cluster1.k3fvpdq.mongodb.net/")
db = client['test']
mechanics_collection = db['mechanic']
collection = db['test_location']  # Replace 'mechanics' with your actual collection name
mechanics_collection.create_index([("coordinates1", "2dsphere")])


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
            
            # Combine data from MongoDB and Firestore into a single response
            combined_data = {
                'name': firestore_details.get('fullName', 'N/A'),
                'contact': firestore_details.get('contact', 'N/A'),
                'profilepicurl': firestore_details.get('profilePicURL', 'N/A'),
                'category': firestore_details.get('catergory', 'N/A'),
                'location': mechanic.get('Area', 'N/A'),
                'address': mechanic.get('Address', 'N/A'),
                'uid': mechanic.get('firebase_uid', 'N/A')
            }
            
            mechanics_list.append(combined_data)

        # Return the list of mechanics with combined data as JSON response
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
        return jsonify({"error": "Failed to convert address to coordinates or address is not provided"}), 400


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



#create appointment connected with vehicle database

@app.route('/create_appointment', methods=['POST'])
def create_appointment():
    data = request.json
    user_uid = data.get('user_uid')

    # Check if user_uid exists in the vehicle collection
    vehicle_data = db.vehicle.find_one({'user_uid': user_uid})
    if not vehicle_data:
        return jsonify({'error': 'User not found in the vehicle database'})

    # Extract vehicle_brand and vehicle from vehicle_data
    vehicle_brand = vehicle_data.get('vehicle_brand')
    vehicle = vehicle_data.get('vehicle')

    # Create appointment
    appointment_data = {
        'Appointments_time': data.get('Appointments_time'),
        'Date_of_appointment': data.get('Date_of_appointment'),
        'user_uid': user_uid,
        'Service_Required': data.get('Service_Required'),
        'vehicle_brand': vehicle_brand,
        'vehicle': vehicle,
        'Mech_uid': data.get('Mech_uid')
    }

    # Insert appointment into the appointment collection
    appointment_id = db.appointment.insert_one(appointment_data).inserted_id

    return jsonify({'success': True, 'appointment_id': str(appointment_id)})






    



api.add_resource(AppointmentResource, '/appointment')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
