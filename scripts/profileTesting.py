from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb+srv://senadi20220678:%23abc%40123@vehicle-repairo.dlhnhh6.mongodb.net/")
db = client['Vehicle_Repairo']
mechanics_collection = db['mechanic_average_rating']

# Function to get mechanic's average rating
def get_mechanic_average_rating(mechanic_id):
    mechanic = mechanics_collection.find_one({'mechanic_id': mechanic_id})
    if mechanic:
        return mechanic.get('average_rating', 0)
    else:
        return None

if __name__ == "__main__":
    mechanics = mechanics_collection.find()
    for mechanic in mechanics:
        mechanic_id = mechanic.get('mechanic_id')
        average_rating = get_mechanic_average_rating(mechanic_id)
        if average_rating is not None:
            print(f"Mechanic ID {mechanic_id} - Average rating ({average_rating})")
        else:
            print(f"Mechanic ID {mechanic_id} - Average rating (Not available)")
