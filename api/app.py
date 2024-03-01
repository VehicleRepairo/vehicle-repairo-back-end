from flask import Flask, jsonify, request
from mongoengine import connect
from pymongo import MongoClient
import os
from dotenv import load_dotenv,find_dotenv
from models.entities.mechanic import Mechanic
from models.entities.vehicle import Vehicle
from geopy.geocoders import Nominatim
from flask_cors import CORS


load_dotenv(find_dotenv())
password = os.environ.get("MONGODB_PWD")


app = Flask(__name__)
CORS(app) 
client = MongoClient(f"mongodb+srv://devindhigurusinghe:{password}.@cluster1.k3fvpdq.mongodb.net/")
db = client['test']
mechanics_collection = db['mechanic']
connect(host=f"mongodb+srv://devindhigurusinghe:{password}.@cluster1.k3fvpdq.mongodb.net/")

@app.route('/nearest_mechanics', methods=['GET'])
def get_nearest_mechanics():
    user_longitude = 6.9778284
    user_latitude = 79.9271523

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
    }
}

    # Execute the query and limit to 2 results
    nearest_mechanics = mechanics_collection.find(query)

    # Convert ObjectId to string before jsonify
    nearest_mechanics_list = []
    for mechanic in nearest_mechanics:
        mechanic['_id'] = str(mechanic['_id'])  # Convert ObjectId to string
        nearest_mechanics_list.append(mechanic)

    if nearest_mechanics_list:
        return jsonify(nearest_mechanics_list)
    else:
        return jsonify({"message": "No mechanics found near your location"}), 404

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

#convert address to coordinates
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
    print(geo_location)

    if geo_location:
        latitude = geo_location.latitude
        longitude = geo_location.longitude

        # Check if firebase_uid exists
        existing_user = db['user_locations'].find_one({'firebase_uid': firebase_uid})

        update_data = {}

        if existing_user:
            # Update coordinates if firebase_uid exists
            update_data['coordinates'] = {
                'type': 'Point',
                'coordinates': [longitude, latitude]
            }

        if address:
            update_data['Area'] = address

        if location:
            update_data['Address'] = location

        if update_data:
            db['user_locations'].update_one(
                {'firebase_uid': firebase_uid},
                {'$set': update_data}
            )

            return jsonify({"message": "Database updated successfully"}), 200
        else:
            return jsonify({"error": "No data provided to update"}), 400
    else:
        return jsonify({"error": "Failed to convert address to coordinates"}), 400


@app.route('/location', methods=['POST'])
def get_location():
    data = request.json
    uid = data.get('uid')
    
    existing_user = db['user_locations'].find_one({'firebase_uid': uid})
    
    if existing_user:
        city = existing_user.get('Area', '')
        location = existing_user.get('Address', '')
        return jsonify({"city": city, "address": location}), 200
    else:
        return jsonify({"message": "Enter your location"}), 404




if __name__ == '__main__':
    app.run(debug=True, port=8000)