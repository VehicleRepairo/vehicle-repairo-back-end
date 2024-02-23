from flask import Flask, request
from flask_restful import Resource, Api
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv, find_dotenv
import json

app = Flask(__name__)
api = Api(app)

#Setting up the MongoDB connection
connection_string = "mongodb+srv://nanthushan:nanthushan123@vehiclerepairo.rprebky.mongodb.net/?retryWrites=true&w=majority&appName=VehicleRepairo"
client = MongoClient(connection_string)

db = client.VehicleRepairoDb

appointments_collection = db.appointments

def create_appointment():
    user = []
    vehicle_brand = []
    vehicle_model = []
    Date_of_appointment = []
    Appointment_time = []
    Service_required = []
    
    #for user, vehicle_brand, vehicle_model, Date_of_appointment, Appointment_time, Service_required in :
     #   appointments_collection.insert_one()


create_appointment()

"""
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
        
api.add_resource(AppointmentResource, '/appointment/<string:appointment_id>')

if __name__ == '__main__':
    app.run(debug=True)
"""