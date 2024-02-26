import pymongo
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
            matching_rows.append(document)
            matching_rows.append("\n\n ---------------------------------------\n\n")

    if not matching_rows:
        print(f"Word '{target_word}' not found in the table.")

    return matching_rows

def main():
    # Connect to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")  
    db = client["problems"] 
    collection = db["guidelines"]  

    word_to_find = input("Enter the word to search: ")

    result_rows = find_word_in_table(collection, word_to_find)

    if result_rows:
        print(f"Documents containing the word '{word_to_find}' in the collection:")
        for document in result_rows:
            print(document)

if __name__ == "__main__":
    nltk.download('stopwords')
    nltk.download('punkt')
    main()
