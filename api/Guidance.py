from flask import Flask, request, jsonify
import pymongo
from rake_nltk import Rake
import nltk
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
def find_word_in_table(collection, target_word):
    matching_rows = []
    rake = Rake()  # Initialize RAKE

    # Iterate through documents in the collection
    for document in collection.find():
        document_text = ' '.join(str(value) for value in document.values() if isinstance(value, str))
        rake.extract_keywords_from_text(document_text)  # Extract keywords from document text
        keywords = rake.get_ranked_phrases()  # Get ranked keywords

        # Check if target word is in any of the keywords
        if any(target_word.lower() in keyword.lower() for keyword in keywords):
            matching_rows.append(document)

    return matching_rows

@app.route('/')
def index():
    return 'Welcome to my Flask application!'

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    search_query = data.get('searchText', '')

    # Connect to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["problems"]
    collection = db["guidelines"]

    result_rows = find_word_in_table(collection, search_query)

    response = {
        'results': result_rows
    }
    return jsonify(response)

# CORS handling
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

if __name__ == "__main__":
    nltk.download('stopwords')
    nltk.download('punkt')
    app.run(debug=True)  # Run the Flask app
