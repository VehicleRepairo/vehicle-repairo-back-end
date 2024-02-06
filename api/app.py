from flask import Flask, jsonify, request
from mongoengine import connect
from pymongo import MongoClient
import os
from dotenv import load_dotenv,find_dotenv
from scripts.entities.mechanic import Mechanic
load_dotenv(find_dotenv())
password = os.environ.get("MONGODB_PWD")


app = Flask(__name__)
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
    

if __name__ == '__main__':
    app.run(debug=True, port=8000)
