from flask import Flask, request, jsonify
from flask_cors import CORS
import pymongo
from bson import ObjectId
from rake_nltk import Rake
import nltk



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
            # Convert ObjectId to string
            document['_id'] = str(document['_id'])
            matching_rows.append(document)

    return matching_rows

    
    
