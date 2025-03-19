# /backend/app.py (create_app function): Creates a Flask application with security and utility extensions.
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from backend.routes.EtlUpload import etl_upload_bp  # Use absolute import



def create_app():
    app = Flask(__name__)

    # Apply CORS to the entire app
    CORS(app, resources={r"/*": {
        "origins": "http://localhost:5174",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": "*",
        "supports_credentials": True
    }})

    # Register blueprint
    app.register_blueprint(etl_upload_bp, url_prefix="/etl")

    @app.route("/")
    @cross_origin(origins="http://localhost:5173", supports_credentials=True)
    def home():
        return jsonify({"message": "Welcome to the ETL API"})

    @app.route("/health")
    def health_check():
        return jsonify({"status": "healthy"}), 200
    

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))  # Get PORT from environment variable
    app.run(host="0.0.0.0", port=port, debug=False)  # Set debug=False for production







# import os
# import sys
# sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
# # from routes.EtlUpload import etl_upload_bp  # Import the blueprint
# from backend.routes.EtlUpload import etl_upload_bp  # Use absolute import


# from flask import Flask, jsonify, request
# from flask_cors import CORS
# from flask_talisman import Talisman #// Talisman is a security extension for Flask applications that adds various HTTP security headers to responses.
# from flask_limiter import Limiter # Limiter is a rate limiting extension for Flask applications.
# from config import config
# import logging # The logging module is used to log messages for debugging and monitoring purposes.
# # from backend.routes import db_routes, file_routes, ai_routes
# sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# def create_app():
#     app = Flask(__name__)
#     CORS(app)  # This enables CORS for all routes
#     app.register_blueprint(etl_upload_bp, url_prefix="/etl")
#     @app.route("/")
#     @cross_origin() # allow all origins all methods.
#     # app.config.from_object(config[config_name])
    
#     # Security extensions
#     # CORS(app, resources={r"/*": {"origins": "*"}})
#     # Talisman(app, content_security_policy=app.config['CSP'])
#     # Limiter(app, default_limits=["200 per day", "50 per hour"])
    
#     # Setup upload folder
#     # if not os.path.exists(app.config['UPLOAD_FOLDER']):
#     #     os.makedirs(app.config['UPLOAD_FOLDER'])
    
#     # Register blueprints
#     # app.register_blueprint(etl_upload_bp, url_prefix="/etl")

#     # app.register_blueprint(db_routes.db_routes)
#     # app.register_blueprint(file_routes.file_routes)
#     # app.register_blueprint(ai_routes.ai_routes)
    
#     # # Configure logging
#     # logging.basicConfig(
#     #     level=logging.INFO,
#     #     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#     # )
    
#     # @app.route('/health')
#     # def health_check():
#     #     return jsonify({'status': 'healthy'}), 200
    
#     # return app
    
#   # Register the blueprint
    

# # if __name__ == '__main__':
# #     app = create_app()
# #     app.run(port=5000,debug=True)


#     # Register blueprints
#     app.register_blueprint(etl_upload_bp, url_prefix="/etl")

#     @app.route('/health')
#     def health_check():
#         return jsonify({'status': 'healthy'}), 200

#     return app  # <-- Make sure to return the app instance

# if __name__ == '__main__':
#     app = create_app()
#     app.run(port=5000, debug=True)


'''The provided code is a Flask application setup with several security and utility extensions. Here's a summary of the key components, their purpose, and usage:

Key Components
Flask Application (create_app function):

Initializes a Flask application.
Configures the app using a configuration object.
Sets up security extensions: CORS, Talisman, and Limiter.
Creates necessary directories for file uploads.
Registers blueprints for different routes.
Configures logging.
Defines a health check endpoint.
Security Extensions:

CORS: Enables Cross-Origin Resource Sharing to allow or restrict resources on a web server to be requested from another domain.
Talisman: Adds various HTTP security headers to Flask responses to enhance security.
Limiter: Implements rate limiting to control the rate of requests to the application.
Utility Functions and Classes:

from_object: Loads configuration from an object or module.
exists and makedirs: Utility functions to check for the existence of a path and create directories, respectively.
register_blueprint: Registers a blueprint with the Flask application.
basicConfig: Configures logging.
route: Decorator to register a view function for a given URL rule.
jsonify: Converts Python objects to JSON responses.
run: Runs the Flask application.
Usage
Creating the Flask Application:

Running the Application:

Defining Routes:

Using Blueprints:

Purpose
Security: The application uses CORS, Talisman, and Limiter to enhance security by controlling cross-origin requests, adding security headers, and limiting the rate of requests.
Configuration Management: The from_object method allows loading configuration from different sources, making the app flexible and configurable.
Logging: Configures logging to help with debugging and monitoring the application.
Health Check: Provides a health check endpoint to monitor the application's status.
This setup ensures that the Flask application is secure, configurable, and easy to maintain.

'''

