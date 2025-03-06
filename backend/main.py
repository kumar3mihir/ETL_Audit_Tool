from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow CORS for all routes

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure upload directory exists
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route('/')
def home():
    return '''
    <h1>Welcome to the Metadata Extraction API</h1>
    <p>Use the <b>/extract_metadata</b> endpoint to upload CSV or Excel files.</p>
    <p>Try sending a POST request with one or more files to see the extracted metadata!</p>
    '''

@app.route('/extract_metadata', methods=['POST'])
def extract_metadata():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    files = request.files.getlist('file')  # Get multiple files

    if not files or all(file.filename == '' for file in files):
        return jsonify({"error": "No selected file"}), 400

    all_metadata = []  # Store metadata for multiple files

    for file in files:
        if file.filename == '':
            continue  # Skip empty files

        # Save the file
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        # Process file (Extract metadata)
        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file.filename.endswith('.xlsx'):
                df = pd.read_excel(file_path, engine='openpyxl')
            else:
                return jsonify({"error": f"Unsupported file format: {file.filename}"}), 400

            # Extract metadata
            metadata = {
                "filename": file.filename,
                "columns": list(df.columns),
                "data_types": df.dtypes.astype(str).to_dict(),
                "num_rows": len(df)
            }
            all_metadata.append(metadata)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Metadata extracted successfully!", "metadata": all_metadata})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
