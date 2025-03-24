import os
from numpy import full
import pandas as pd
from flask import Flask, request, jsonify, send_file
from flask import Blueprint
from openai import OpenAI
import json
import uuid
from dotenv import load_dotenv
import zipfile
import xml.etree.ElementTree as ET
from werkzeug.utils import secure_filename  # Import secure_filename
import re
import time
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import openai  # Ensure you're using the correct API client
from flask import send_file
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
import csv
from datetime import datetime
import os
import zipfile
import uuid
import io
import datetime
from flask import Blueprint, request, jsonify
import datetime
import os
import json
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from celery import Celery
import redis
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np



# Define the blueprint
etl_upload_bp = Blueprint("etl_upload", __name__)








# Celery Configuration
celery_app = Celery(
    "etl_tasks",
    backend="redis://localhost:6379/0",
    broker="redis://localhost:6379/0"
)

# Redis Cache for Storing File Metadata
redis_client = redis.StrictRedis(host="localhost", port=6379, db=1, decode_responses=True)





def generate_embeddings(chunks):
    """Generate embeddings using NVIDIA's API."""
    response = client.embeddings.create(
        model="nomic-embed-text",  # NVIDIA's embedding model
        input=chunks
    )
    return np.array([r.embedding for r in response.data], dtype=np.float32)  # Convert to NumPy array




def store_embeddings_in_faiss(embeddings, chunk_texts):
    """Store embeddings in FAISS index."""
    index = faiss.IndexFlatL2(embeddings.shape[1])  # L2 distance index
    index.add(embeddings)
    return index, chunk_texts  # Return index + chunk mapping




def search_relevant_chunks(index, chunk_texts, query, top_k=3):
    """Find the most relevant script chunks based on a query."""
    
    # Generate embedding for query
    query_embedding = generate_embeddings([query])  # Use NVIDIA embedding model
    
    # Search in FAISS index
    distances, indices = index.search(query_embedding, top_k)
    
    # Retrieve relevant script chunks
    relevant_chunks = [chunk_texts[i] for i in indices[0] if i < len(chunk_texts)]
    
    return relevant_chunks


# audit_questions = {
#     "data_pipeline_check": "Does the ETL script follow a layered architecture (Landing, Staging, Final)?",
#     "audit_control_mechanisms": "Does the ETL script capture start/end timestamps, row counts, and have restartability mechanisms?"
# }


audit_questions = {
    "data_pipeline_check": (
        "When ingesting data from sources into the data lake, data warehouse, or ETL pipeline, "
        "does the ETL script follow a layered architecture? Specifically, does it include: "
        "(1) A landing zone where raw data is stored as-is, allowing recovery in case of failure; "
        "(2) Multiple staging layers such as Layer-1 for sanity checks, cleanup, format standardization, "
        "and deduplication, Layer-2 for matching/integration, and Layer-3 for transformations and summarization; "
        "(3) A final layer where the processed data is stored in the target data lake or warehouse?"
    ),
    
    "audit_control_mechanisms": (
        "Does the ETL script implement proper audit, balance, and control mechanisms? "
        "Specifically, does it capture operational metadata, including start and end timestamps, "
        "the number of rows read and written, and processing duration? Additionally, does the ETL pipeline: "
        "(1) Ensure data reconcilability by checking whether data movement from source to target is explainable; "
        "(2) Include a restartability mechanism to resume from the last failure point instead of restarting from scratch; "
        "(3) Implement robust exception handling, including sanity checks, anomaly detection, validation checks, "
        "and appropriate alerts for failures?"
    )
}

from datetime import datetime

def analyze_etl_script(script_chunks, question_key, filename, file_ext):
    """Send relevant script chunks to GenAI for auditing."""
    
    # Generate timestamps
    audit_start_time = datetime.now().strftime("%d-%m-%Y %H:%M")

    # Retrieve the relevant audit question
    question = audit_questions.get(question_key, "Invalid question key")

    # Find relevant script chunks
    relevant_chunks = search_relevant_chunks(faiss_index, stored_chunks, question)

    # Construct structured prompt with context
    structured_prompt = f"""
    [CONTEXT]: The following ETL script chunks are extracted:
    {relevant_chunks}

    [QUESTION]: {question}
    """

    # Call NVIDIA GenAI API (LLaMA-3.3-70B)
    response = call_genai_api(structured_prompt)

    # Process streamed response
    audit_result = "".join(chunk.choices[0].delta.content for chunk in response)

    # Generate end timestamp
    audit_end_time = datetime.now().strftime("%d-%m-%Y %H:%M")

    # Construct the audit report
    audit_report = {
        "Audit Start Date & Time": audit_start_time,
        "Audit End Date & Time": audit_end_time,
        "File Type": file_ext,
        "File Name Full Path": filename,
        "Audit Status": "Completed",
        "Audit Result": "Pass" if "YES" in audit_result else "Fail",
        "Audit Details": audit_result
    }

    return audit_report



# new acc zero usage apikey =  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
# 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
# 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
# Configure Nvidia API
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    # api_key=os.getenv("apikey_nvidia")
   api_key="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"
)


# API Retry Logic: Retries up to 3 times with exponential backoff
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_genai_api(prompt):
    print("Calling GenAI API...")

    completion = client.chat.completions.create(
        model="meta/llama-3.3-70b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        top_p=0.5,
        max_tokens=4096,
        stop=["Let's analyze", "Starting with"],
        stream=True
    )
    
    return completion  # Return API response




def extract_zip_memory(zip_file):
    """
    Extracts valid files from a ZIP archive in-memory.

    Args:
        zip_file (FileStorage): Uploaded ZIP file.

    Returns:
        list: List of (filename, file extension, file content).
    """
    extracted_files = []
    allowed_extensions = {".py", ".sql", ".sh", ".txt", ".yaml", ".yml", ".json", ".xml",
                          ".csv", ".java", ".ipynb", ".bat", ".ps1", ".pl", ".rb", ".php",
                          ".r", ".scala", ".go", ".c", ".cpp", ".ts", ".js"}

    try:
        with zipfile.ZipFile(io.BytesIO(zip_file.read()), "r") as zip_ref:
            for file_name in zip_ref.namelist():
                file_ext = os.path.splitext(file_name)[1].lower()

                # Skip invalid files
                if file_ext not in allowed_extensions or file_name.startswith("."):
                    continue  

                # Read file content in memory
                with zip_ref.open(file_name) as f:
                    content = f.read().decode(errors="ignore")
                    extracted_files.append((file_name, file_ext, content))

                print(f"Extracted: {file_name}, Type: {file_ext}, Content Sample: {content[:100]}")

    except zipfile.BadZipFile:
        print("Error: Invalid ZIP file.")

    return extracted_files





def chunk_etl_script(content: str, file_extension: str):
    """
    Breaks ETL scripts into chunks based on file type.
    
    Args:
        content (str): File content as a string.
        file_extension (str): Extension of the file.

    Returns:
        List[Tuple[int, str]]: List of (chunk_id, chunk_content).
    """
    chunks = []

    if file_extension in {".py", ".java", ".c", ".cpp", ".js", ".ts", ".scala", ".rb", ".php", ".r"}:
        # Split by function/method definitions
        chunks = re.split(r"\n\s*(def |class |\w+\s*\()", content)
    
    elif file_extension in {".sql", ".hql", ".bql", ".spark"}:
        # Split by SQL statements (ending with `;`)
        chunks = re.split(r";\s*\n", content)
    
    elif file_extension in {".yaml", ".yml"}:
        # Split YAML by sections (keys starting at column 0)
        chunks = re.split(r"\n(?=[^\s])", content)
    
    elif file_extension in {".json"}:
        # Split JSON by top-level keys
        chunks = re.findall(r'(\s*".+?":\s*{.*?})', content, re.DOTALL)
    
    elif file_extension in {".csv"}:
        # Split CSV into chunks of rows (e.g., every 100 rows)
        rows = content.split("\n")
        chunk_size = 100  # Adjust as needed
        chunks = [ "\n".join(rows[i:i+chunk_size]) for i in range(0, len(rows), chunk_size) ]
    
    else:
        # General fallback: Split by paragraph or sentences
        chunks = re.split(r"(?<=[.!?])\s+", content)

    # Assign a unique ID to each chunk
    return [(i, chunk.strip()) for i, chunk in enumerate(chunks) if chunk.strip()]





etl_upload_bp = Blueprint("etl_upload", __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    ".py", ".sql", ".sh", ".yaml", ".yml", ".json", ".csv", ".xml",
    ".java", ".ipynb", ".bat", ".ps1", ".pl", ".rb", ".php", ".r",
    ".scala", ".go", ".c", ".cpp", ".ts", ".js", ".hql", ".pig",
    ".bql", ".spark", ".pyspark", ".airflow", ".nifi", ".oozie",
    ".dag", ".toml", ".ini", ".properties", ".cfg", ".parquet",
    ".avro", ".orc", ".xls", ".xlsx", ".rmd"
}


def allowed_file(filename):
    """Check if the file extension is allowed."""
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS


@etl_upload_bp.route("/upload", methods=["POST"])
def upload_file():
    """Handles file upload and extracts metadata before sending for processing."""
    
    file = request.files.get("file")
    if not file:
        print("[ERROR] No file provided.")
        return jsonify({"error": "No file provided"}), 400

    filename = secure_filename(file.filename)
    file_ext = os.path.splitext(filename)[1].lower()

    if not allowed_file(filename):
        print(f"[ERROR] Unsupported file type: {file_ext}")   #here later include to skip unsupported file types
        return jsonify({"error": "Unsupported file type"}), 400

    audit_start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    extracted_files = []

    print(f"[INFO] Received file: {filename}, Type: {file_ext}")

    try:
        if file_ext == ".zip":
            extracted_files = extract_zip_memory(file)
            if not extracted_files:
                print("[ERROR] ZIP extracted but contains no valid files")
                return jsonify({"error": "ZIP extracted but contains no valid files"}), 400
        else:
            extracted_files = [(filename, file_ext, file.stream.read().decode(errors="ignore"))]  # Read in-memory

        audit_end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Print extracted files for debugging
        for name, ext, content in extracted_files:
            print(f"[INFO] Processed File: {name}, Extension: {ext}, First 100 chars: {content[:100]}")

        # Queue for asynchronous processing (Send only script content)
        for name, ext, content in extracted_files:
            task = process_etl_file.apply_async(args=[name, ext, content])

            # Store task metadata in Redis for tracking
            redis_client.set(f"task:{task.id}", json.dumps({
                "filename": name,
                "extension": ext,
                "status": "queued",
                "audit_start_time": audit_start_time,
                "audit_end_time": audit_end_time
            }))

        return jsonify({
            "message": "Files queued for processing.",
            "audit_start_time": audit_start_time,
            "audit_end_time": audit_end_time,
            "processed_files": [{"name": f[0], "type": f[1]} for f in extracted_files]
        }), 202  # 202 Accepted (Processing in Background)

    except Exception as e:
        print(f"[ERROR] Exception in file upload: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500


# from celery import shared_task

# @shared_task
@celery_app.task(bind=True)
def process_etl_file(self, filename, file_ext, content):
    """Celery task to process ETL script file in the background."""
    print(f"[TASK] Processing File: {filename}, Type: {file_ext}")

    try:
        # Step 1: Extract script chunks
        script_chunks = chunk_etl_script(content, file_ext)
        if not script_chunks:
            print(f"[WARNING] No valid chunks found in {filename}. Skipping analysis.")
            redis_client.set(f"result:{self.request.id}", json.dumps({
                "filename": filename,
                "extension": file_ext,
                "audit_results": [],
                "status": "skipped"
            }))
            return {"filename": filename, "audit_results": [], "status": "skipped"}

        print(f"[INFO] Extracted {len(script_chunks)} chunks from {filename}.")

        # Step 2: Generate and store embeddings
        embeddings = generate_embeddings(script_chunks)
        global faiss_index, stored_chunks
        faiss_index, stored_chunks = store_embeddings_in_faiss(embeddings, script_chunks)

        # Step 3: Analyze ETL script using NVIDIA GenAI (LLaMA-3)
        audit_results = analyze_etl_script(script_chunks)

        # Step 4: Store results in Redis for retrieval
        redis_client.set(f"result:{self.request.id}", json.dumps({
            "filename": filename,
            "extension": file_ext,
            "audit_results": audit_results,
            "status": "completed"
        }))

        print(f"[TASK COMPLETE] File {filename} processed successfully.")
        return {"filename": filename, "audit_results": audit_results, "status": "completed"}

    except Exception as e:
        print(f"[ERROR] Exception while processing {filename}: {str(e)}")
        redis_client.set(f"result:{self.request.id}", json.dumps({
            "filename": filename,
            "extension": file_ext,
            "audit_results": [],
            "status": "failed",
            "error": str(e)
        }))
        return {"filename": filename, "audit_results": [], "status": "failed", "error": str(e)}






celery_app.conf.update(
    include=["backend.routes.EtlUpload"]  # Ensure Celery registers this module
)


