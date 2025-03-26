# /backend/routes/Extract_metadata/mongo_extract.py
from flask import Blueprint, jsonify
from pymongo import MongoClient
import certifi

# Define Blueprint for modular routing
mongo_extract_bp = Blueprint('mongo_extract', __name__)

# MongoDB Connection
MONGO_URI = "mongodb+srv://kumarmihir626:EAbAm1eEWkcnzjmI@cluster0.hyejt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

@mongo_extract_bp.route('/extract-mongodb-metadata', methods=['GET'])
def extract_metadata():
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())  # Connect to MongoDB
    db = client["etl_metadata"]  # Database name
    
    metadata = {}
    
    # Get all collection names (tables)
    collections = db.list_collection_names()
    
    for collection in collections:
        sample_doc = db[collection].find_one()  # Fetch one document to infer schema
        metadata[collection] = list(sample_doc.keys()) if sample_doc else []
    
    client.close()  # Close connection after operation
    return jsonify(metadata)
