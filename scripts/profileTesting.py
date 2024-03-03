from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb+srv://senadi20220678:%23abc%40123@vehicle-repairo.dlhnhh6.mongodb.net/")
db = client['Ratings_and_Reviews']
# collection = db['ratings']
mechanics_collection = db['mechanics']

# Function to get mechanic's average rating
def get_mechanic_average_rating(mechanic_id):
    mechanic = mechanics_collection.find_one({'mechanic_id': mechanic_id})
    if mechanic:
        return mechanic.get('average_rating', 0)
    else:
        return None

if __name__ == "__main__":
    mechanic_id = input("Enter the Mechanic ID : ")
    average_rating = get_mechanic_average_rating(mechanic_id)
    
    if average_rating is not None:
        print("Mechanic ID:", mechanic_id)
        print("Average Rating:", average_rating)
    else:
        print("Mechanic not found.")
