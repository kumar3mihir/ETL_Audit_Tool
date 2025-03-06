# /backend/routes/db_routes.py: Contains routes for handling database connections and schema retrieval.
from flask import Blueprint, request, jsonify
from config import Config
from db_connectors import DatabaseConnector
import logging

db_routes = Blueprint('db', __name__, url_prefix='/api/db')

@db_routes.route('/connect', methods=['POST'])
def handle_db_connection():
    """Handle database connection parameters"""
    try:
        data = request.get_json()
        db_type = data.get('type')
        connection_params = data.get('params')
        
        if db_type not in Config.DATABASE_TYPES:
            return jsonify({'error': 'Invalid database type'}), 400
            
        # Encrypt credentials before storage
        encrypted_params = Config.CIPHER_SUITE.encrypt(str(connection_params).encode())
        
        connector = DatabaseConnector(db_type)
        success, message = connector.connect(encrypted_params.decode())
        
        if success:
            return jsonify({
                'status': 'connected',
                'schema': connector.get_schema()
            }), 200
        return jsonify({'error': message}), 400
        
    except Exception as e:
        logging.error(f"Connection error: {str(e)}")
        return jsonify({'error': 'Database connection failed'}), 500

@db_routes.route('/test', methods=['POST'])
def test_connection():
    """Test database connection before saving"""
    try:
        data = request.get_json()
        db_type = data.get('type')
        params = data.get('params')
        
        connector = DatabaseConnector(db_type)
        success, message = connector.connect(params)
        
        return jsonify({'success': success, 'message': message}), 200
        
    except Exception as e:
        logging.error(f"Test connection error: {str(e)}")
        return jsonify({'error': 'Connection test failed'}), 500

@db_routes.route('/schema', methods=['POST'])
def get_schema():
    """Retrieve database schema"""
    try:
        data = request.get_json()
        db_type = data.get('type')
        encrypted_params = data.get('params')
        
        connector = DatabaseConnector(db_type)
        success, message = connector.connect(encrypted_params)
        
        if success:
            schema = connector.get_schema()
            return jsonify(schema), 200
        return jsonify({'error': message}), 400
        
    except Exception as e:
        logging.error(f"Schema extraction error: {str(e)}")
        return jsonify({'error': 'Schema extraction failed'}), 500





'''The provided code is a Flask-based backend that handles database connections and schema retrieval. Here's a summary of the key components and their purposes:

Key Components
Blueprint Definition (db_routes):

db_routes is a Flask Blueprint that groups related routes under the /api/db URL prefix.
Routes:

/connect: Handles database connection parameters, encrypts them, and attempts to connect to the specified database type.
/test: Tests the database connection with provided parameters without saving them.
/schema: Retrieves the schema of the connected database.
DatabaseConnector Class:

Manages connections to different types of databases (MongoDB, MySQL, SQL Server).
connect: Establishes a connection to the database using decrypted parameters.
get_schema: Retrieves the schema of the connected database.
_get_mongo_schema: Retrieves schema details for MongoDB.
_get_sql_schema: Retrieves schema details for SQL-based databases.
How to Use
Setup Flask Application:

Integrate the db_routes blueprint into your Flask application.
Configuration:

Ensure Config class has the necessary configurations, including DATABASE_TYPES and CIPHER_SUITE for encryption/decryption.
DatabaseConnector:

Use this class to manage database connections and retrieve schemas. Instantiate it with the database type and call its methods as needed.
Purpose
Database Connection Management: Securely handle and test database connections using encrypted parameters.
Schema Retrieval: Provide endpoints to retrieve the schema of connected databases, useful for applications that need to understand database structure dynamically.
Example Usage
Connecting to a Database:

Send a POST request to /api/db/connect with JSON payload containing type and params.
Testing a Connection:

Send a POST request to /api/db/test with similar JSON payload to test the connection without saving it.
Retrieving Schema:

Send a POST request to /api/db/schema with JSON payload containing type and encrypted params to get the database schema.
This setup is useful for applications that need to manage multiple database connections securely and dynamically retrieve database schemas.'''