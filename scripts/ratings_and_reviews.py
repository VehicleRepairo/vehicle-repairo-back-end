from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient("mongodb+srv://senadi20220678:%23abc%40123@ratingsandreviews.htgjxi1.mongodb.net/")
db = client['Ratings_and_Reviews']
collection = db['ratings']

# Function to get reviews for a product
def get_reviews(mechanic_id):
    reviews = collection.find({'mechanic_id': mechanic_id})
    return list(reviews)

# Function to get ratings and review from the user
def get_user_input():
    mechanic_id = input("Enter the Mechanic ID : ")
    rating = int(input("Enter the rating (1-5) : "))
    comment = input("Enter your review/comment: ")
    return mechanic_id, rating, comment