from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from pymongo import MongoClient
from bson import ObjectId
import json
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app)

# Setting up the MongoDB connection
connection_string = "mongodb://localhost:27017"
client = MongoClient(connection_string)

# Specify the database
db = client['VehicleRepairo']

# Define collections
appointments_collection = db['appointments']


class AllAppointmentsResource(Resource):
    def get(self):
        appointments = appointments_collection.find()
        if appointments.count() > 0:
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

    def put(self, appointment_id):
        data = request.get_json()
        result = appointments_collection.update_one({'_id': ObjectId(appointment_id)}, {'$set': data})
        if result.modified_count > 0:
            return {'message': 'Appointment updated successfully'}, 200
        else:
            return {'message': 'Appointment not found'}, 404

    def delete(self, appointment_id):
        result = appointments_collection.delete_one({'_id': ObjectId(appointment_id)})
        if result.deleted_count > 0:
            return {'message': 'Appointment deleted successfully'}, 200
        else:
            return {'message': 'Appointment not found'}, 404


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


api.add_resource(AppointmentResource, '/appointment/<string:appointment_id>')

if __name__ == '__main__':
    app.run(debug=True)
