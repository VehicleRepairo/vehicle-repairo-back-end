from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient("mongodb+srv://senadi20220678:%23abc%40123@vehicle-repairo.dlhnhh6.mongodb.net/")
db = client['Vehicle_Repairo']
collection = db['ratings']

# Function to add a new review
def add_review(mechanic_id, rating, comment):
    review = {
        'mechanic_id': mechanic_id,
        'rating': rating,
        'comment': comment,
        'timestamp': datetime.now()
    }
    collection.insert_one(review)

# Function to get reviews for a mechanic
def get_reviews(mechanic_id):
    reviews = collection.find({'mechanic_id': mechanic_id})
    return list(reviews)

# Function to calculate average rating for a mechanic
def calculate_average_rating(mechanic_id):
    reviews = get_reviews(mechanic_id)
    total_ratings = sum(review['rating'] for review in reviews)
    average_rating = total_ratings / len(reviews) if reviews else 0
    return average_rating

# Function to update average rating for a mechanic
def update_average_rating(mechanic_id):
    average_rating = calculate_average_rating(mechanic_id)
    db.mechanic_average_rating.update_one({'mechanic_id': mechanic_id}, {'$set': {'average_rating': average_rating}}, upsert=True)

# Function to get ratings and review from the user
def get_user_input():
    mechanic_id = input("Enter the Mechanic ID : ")
    rating = int(input("Enter the rating (1-5) : "))
    comment = input("Enter your review/comment: ")
    return mechanic_id, rating, comment


if __name__ == "__main__":
    mechanic_id, rating, comment = get_user_input()
    add_review(mechanic_id, rating, comment)
    print("Review added successfully!")
    
    update_average_rating(mechanic_id)

    # Getting reviews for the mechanic
    reviews = get_reviews(mechanic_id)
    print("All reviews for mechanic", mechanic_id)
    for review in reviews:
        print(f"Rating: {review['rating']}, Comment: {review['comment']}, Timestamp: {review['timestamp']}")


    print("Average rating for mechanic", mechanic_id, ":", calculate_average_rating(mechanic_id))
