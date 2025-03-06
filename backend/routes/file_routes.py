# /backend/routes/file_routes.py: Contains routes for handling file uploads and processing.
from flask import Blueprint, request, jsonify
from config import Config
import os
import uuid
import pandas as pd
from werkzeug.utils import secure_filename
import logging
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

file_routes = Blueprint('files', __name__, url_prefix='/api/files')

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@file_routes.route('/upload', methods=['POST'])
def upload_files():
    """Handle batch Excel file uploads"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
            
        files = request.files.getlist('files')
        if len(files) > 10:
            return jsonify({'error': 'Maximum 10 files allowed'}), 400

        upload_dir = Config.UPLOAD_FOLDER
        os.makedirs(upload_dir, exist_ok=True)
        
        saved_files = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_name = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(upload_dir, unique_name)
                file.save(file_path)
                saved_files.append({
                    'original_name': filename,
                    'saved_name': unique_name,
                    'path': file_path
                })
                
        return jsonify({'message': 'Files uploaded successfully', 'files': saved_files}), 200
        
    except Exception as e:
        logging.error(f"File upload error: {str(e)}")
        return jsonify({'error': 'File upload failed'}), 500

@file_routes.route('/process', methods=['POST'])
def process_files():
    """Process uploaded Excel files for schema extraction"""
    try:
        data = request.get_json()
        file_ids = data.get('file_ids', [])
        
        results = []
        for file_id in file_ids:
            file_path = os.path.join(Config.UPLOAD_FOLDER, file_id)
            if not os.path.exists(file_path):
                continue
                
            try:
                df = pd.read_excel(file_path, sheet_name=None)
                schema = {
                    'sheets': [],
                    'columns': {},
                    'data_types': {}
                }
                
                for sheet_name, sheet_data in df.items():
                    schema['sheets'].append(sheet_name)
                    schema['columns'][sheet_name] = list(sheet_data.columns)
                    schema['data_types'][sheet_name] = sheet_data.dtypes.apply(lambda x: x.name).to_dict()
                    
                results.append({
                    'file_id': file_id,
                    'schema': schema
                })
            except Exception as e:
                logging.error(f"Error processing {file_id}: {str(e)}")
                
        return jsonify({'results': results}), 200
        
    except Exception as e:
        logging.error(f"Processing error: {str(e)}")
        return jsonify({'error': 'File processing failed'}), 500

def generate_pdf_report(data, filename):
    """Generate PDF report using ReportLab"""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Add title
    story.append(Paragraph("Metadata Analysis Report", styles['Title']))
    story.append(Spacer(1, 12))
    
    # Add content
    for section in data:
        story.append(Paragraph(section['title'], styles['Heading2']))
        for item in section['content']:
            story.append(Paragraph(f"- {item}", styles['BodyText']))
        story.append(Spacer(1, 8))
        
    doc.build(story)
    return filename






'''This code defines a Flask blueprint for handling file uploads and processing in a web application. Here's a summary of the key components and their purposes:

Imports
Various modules are imported, including Flask components, configuration, file handling utilities, and libraries for handling Excel files and generating PDFs.
Blueprint Definition
file_routes is defined as a Flask blueprint with the URL prefix /api/files.
Constants
ALLOWED_EXTENSIONS specifies the allowed file extensions for uploads (xlsx and xls).
Helper Functions
allowed_file(filename): Checks if a file has an allowed extension.
generate_pdf_report(data, filename): Generates a PDF report using ReportLab.
Routes
Upload Files

Endpoint: /upload
Method: POST
Function: upload_files()
Purpose: Handles batch uploads of Excel files, saves them with unique names, and returns a JSON response with the details of the saved files.
Process Files

Endpoint: /process
Method: POST
Function: process_files()
Purpose: Processes uploaded Excel files to extract schema information (sheets, columns, data types) and returns a JSON response with the results.
Error Handling
Both routes include try-except blocks to log errors and return appropriate error messages in JSON format.
Usage
This blueprint can be used in a Flask application to handle file uploads and processing, particularly for Excel files. It provides endpoints for uploading files and processing them to extract metadata, which can be useful in applications that need to analyze or transform Excel data.
Example Integration
To integrate this blueprint into a Flask application, you would register it with the Flask app instance:

This setup allows the application to handle file uploads and processing via the defined endpoints.'''