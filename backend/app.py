from backend.routes.EtlUpload import etl_upload_bp  # Ensure this import works
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin

def create_app():
    app = Flask(__name__)

    # Apply CORS
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

# Explicitly create an app instance for Gunicorn
app = create_app()  # ✅ Gunicorn will now work with "app"