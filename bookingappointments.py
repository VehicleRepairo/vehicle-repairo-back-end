from flask import Flask, request
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

    def delete(self, appointment_id):
        result = appointments_collection.delete_one({'_id': ObjectId(appointment_id)})
        if result.deleted_count > 0:
            return {'message': 'Appointment deleted successfully'}, 200
        else:
            return {'message': 'Appointment not found'}, 404
        
api.add_resource(AppointmentResource, '/appointment')

if __name__ == '__main__':
    app.run(debug=True)
