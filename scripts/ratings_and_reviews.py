from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient("mongodb+srv://senadi20220678:%23abc%40123@ratingsandreviews.htgjxi1.mongodb.net/")
db = client['Ratings_and_Reviews']
collection = db['ratings']

