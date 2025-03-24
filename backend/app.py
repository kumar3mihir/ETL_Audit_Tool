import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
from backend.routes.EtlUpload import etl_upload_bp, celery_app  # Import Celery app
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin

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

    # Attach Flask app context to Celery
    celery_app.conf.update(app.config)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)