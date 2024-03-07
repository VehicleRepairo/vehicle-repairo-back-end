from flask import Flask, jsonify, request
from pymongo import MongoClient
import os
from Persistance.mechanic import Mechanic
from Persistance.vehicle import Vehicle
from flask_cors import CORS
from flask_restful import Resource,Api
from bson import ObjectId
import json
import ratings_and_reviews

app = Flask(__name__)
CORS(app) 
api = Api(app)


#mongodb connection
client = MongoClient("mongodb://localhost:27017")
db = client['Vehicle_Repairo']
mechanics_collection = db['mechanic']
vehicle_collection = db['vehicle']
appointments_collection = db['appointment']
users_collection = db['users']

mechanics_collection.create_index([("coordinates1", "2dsphere")])
appointments_collection.create_index({ "Mech_uid": 1 })


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
    db.vehicle_collection.insert_one(vehicle_data)

    return jsonify({"message": "Vehicle created successfully"}), 201


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
    print(user_uid)


    # Create appointment
    appointment_data = {
        'Appointments_time': data.get('Appointments_time'),
        'Date_of_appointment': data.get('Date_of_appointment'),
        'Name':data.get('Name'),
        'user_uid': user_uid,
        'contact': data.get('contact'),
        'Service_Required': data.get('Service_Required'),
        'vehicle':data.get('vehicle') ,
        'Mech_uid': data.get('Mech_uid'),
        'Appointment_status':"Pending"

    }

    # Insert appointment into the appointment collection
    appointment_id = db.appointment.insert_one(appointment_data).inserted_id

    return jsonify({'success': True, 'appointment_id': str(appointment_id)})




@app.route('/appointments/<mechanic_uid>', methods=['GET'])
def get_appointments_by_mechanic_uid(mechanic_uid):
    # Assuming mechanic_uid is a string
    appointments = appointments_collection.find({'Mech_uid': mechanic_uid})

    # Convert MongoDB cursor to list of dictionaries
    appointments_list = list(appointments)

    # Convert ObjectId to string in each appointment dictionary
    for appointment in appointments_list:
        appointment['_id'] = str(appointment['_id'])

    return jsonify(appointments_list)



# Route to delete appointment
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
            'appointment_status': 'Deleted'
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
        return jsonify({'message': 'Internal server error'}), 500
    



@app.route('/appointments/<string:appointment_id>', methods=['PATCH'])
def update_appointment_status(appointment_id):
    try:
        # Extract updated appointment status from the request body
        data = request.json
        appointment_status = data.get('Appointment_status')
        
        # Update appointment status in the database
        result = appointments_collection.update_one(
            {'_id': ObjectId(appointment_id)},
            {'$set': {'Appointment_status': appointment_status}}
        )
        
        if result.modified_count == 1:
            return jsonify({'message': 'Appointment status updated successfully'}), 200
        else:
            return jsonify({'message': 'Appointment not found'}), 404
    except Exception as e:
        print("Error:", e)
        return jsonify({'message': 'Internal server error'}), 500




api.add_resource(AppointmentResource, '/appointment')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
