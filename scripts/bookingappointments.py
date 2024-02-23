from flask import Flask, request
from flask_restful import Resource, Api
from pymongo import MongoClient
from bson import ObjectId
import json

app = Flask(__name__)
api = Api(app)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['VehicleRepairo']

# Define collections
mechanics_collection = db['mechanics']
appointments_collection = db['appointments']


class MechanicResource(Resource):
    def get(self, mechanic_id):
        mechanic = mechanics_collection.find_one({'_id': ObjectId('65a291684180b5ac6d8ae6fe')})
        if mechanic:
            return json.loads(json.dumps(mechanic, default=str)), 200
        else:
            return {'message': 'Mechanic not found'}, 404

    def post(self):
        data = request.get_json()
        mechanic_id = mechanics_collection.insert_one(data).inserted_id
        return {'mechanic_id': str(mechanic_id)}, 201

    def put(self, mechanic_id):
        data = request.get_json()
        result = mechanics_collection.update_one({'_id': ObjectId('65a291684180b5ac6d8ae6fe')}, {'$set': data})
        if result.modified_count > 0:
            return {'message': 'Mechanic updated successfully'}, 200
        else:
            return {'message': 'Mechanic not found'}, 404

    def delete(self, mechanic_id):
        result = mechanics_collection.delete_one({'_id': ObjectId('65a291684180b5ac6d8ae6fe')})
        if result.deleted_count > 0:
            return {'message': 'Mechanic deleted successfully'}, 200
        else:
            return {'message': 'Mechanic not found'}, 404

class AppointmentResource(Resource):
    def get(self, appointment_id):
        appointment = appointments_collection.find_one({'_id': ObjectId('65a291fc4180b5ac6d8ae702')})
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
        result = appointments_collection.update_one({'_id': ObjectId('65a291fc4180b5ac6d8ae702')}, {'$set': data})
        if result.modified_count > 0:
            return {'message': 'Appointment updated successfully'}, 200
        else:
            return {'message': 'Appointment not found'}, 404

    def delete(self, appointment_id):
        result = appointments_collection.delete_one({'_id': ObjectId('65a291fc4180b5ac6d8ae702')})
        if result.deleted_count > 0:
            return {'message': 'Appointment deleted successfully'}, 200
        else:
            return {'message': 'Appointment not found'}, 404


api.add_resource(MechanicResource, '/mechanic/<string:mechanic_id>')
api.add_resource(AppointmentResource, '/appointment/<string:appointment_id>')

if __name__ == '__main__':
    app.run(debug=True)
