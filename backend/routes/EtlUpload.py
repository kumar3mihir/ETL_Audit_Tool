# /backend/routes/EtlUpload.py
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

# Define the blueprint
etl_upload_bp = Blueprint("etl_upload", __name__)
load_dotenv()

UPLOAD_FOLDER = "uploads"
EXTRACTED_FOLDER = "extracted_files"
ALLOWED_FILE_EXTENSIONS = ['.py', '.sql', '.txt', '.json', '.xml', '.csv', '.log']  # Define valid ETL script file formats
# OUTPUT_FOLDER = "output"
OUTPUT_FOLDER = "/Users/mihirkumarmallick/Desktop/access_parent/project/output"


os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXTRACTED_FOLDER, exist_ok=True)


def is_valid_etl_file(file_path):
    """Check if the file is an ETL script based on its extension."""
    _, extension = os.path.splitext(file_path)
    return extension.lower() in ALLOWED_FILE_EXTENSIONS


def validate_json(json_file):
    """Try to parse JSON file to check if it is valid."""
    try:
        with open(json_file, 'r') as f:
            json.load(f)  # Try to parse the JSON
        return True
    except (json.JSONDecodeError, IOError):
        return False


def validate_xml(xml_file):
    """Try to parse XML file to check if it is valid."""
    try:
        with open(xml_file, 'r') as f:
            ET.parse(f)  # Try to parse the XML
        return True
    except (ET.ParseError, IOError):
        return False




# script_types = {
#     "py": "Python",
#     "sql": "SQL",
#     "sh": "Shell",
#     "yaml": "YAML",
#     "yml": "YAML",
#     "json": "JSON",
#     "csv": "CSV",
#     "xml": "XML",
#     "java": "Java",
#     "ipynb": "Jupyter Notebook",
#     "bat": "Batch Script",
#     "ps1": "PowerShell Script",
#     "pl": "Perl",
#     "rb": "Ruby",
#     "php": "PHP",
#     "r": "R Script",
#     "scala": "Scala",
#     "go": "Go",
#     "c": "C",
#     "cpp": "C++",
#     "ts": "TypeScript",
#     "js": "JavaScript",
#     "hql": "Hive Query Language",
#     "pig": "Apache Pig Script",
#     "bql": "BigQuery SQL",
#     "spark": "Apache Spark",
#     "pyspark": "PySpark",
#     "airflow": "Apache Airflow DAG",
#     "nifi": "Apache NiFi",
#     "oozie": "Apache Oozie Workflow",
#     "dag": "Directed Acyclic Graph (DAG)",
#     "toml": "TOML Configuration",
#     "ini": "INI Configuration",
#     "properties": "Java Properties File",
#     "cfg": "General Configuration File",
#     "parquet": "Apache Parquet",
#     "avro": "Apache Avro",
#     "orc": "Optimized Row Columnar (ORC)",
#     "xls": "Excel Spreadsheet",
#     "xlsx": "Excel Spreadsheet",
#     "rmd": "R Markdown",
# }

def detect_script_type(file_path):
    """
    Determines the type of ETL script based on the file extension.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: Type of script (Python, SQL, Shell, YAML, JSON, CSV, XML, Java, Jupyter Notebook, or Unknown)
    """
    ext = file_path.lower().split('.')[-1]  # Get file extension in lowercase
    
    script_types = {
        "py": "Python",
        "sql": "SQL",
        "sh": "Shell",
        "yaml": "YAML",
        "yml": "YAML",
        "json": "JSON",
        "csv": "CSV",
        "xml": "XML",
        "java": "Java",
        "ipynb": "Jupyter Notebook",
        "bat": "Batch Script",
        "ps1": "PowerShell Script",
        "pl": "Perl",
        "rb": "Ruby",
        "php": "PHP",
        "r": "R Script",
        "scala": "Scala",
        "go": "Go",
        "c": "C",
        "cpp": "C++",
        "ts": "TypeScript",
        "js": "JavaScript"
    }

    return script_types.get(ext, "Unknown")


def remove_comments(content, file_ext):
    """Removes comments from Python, SQL, JSON, XML, and CSV files."""
    
    if file_ext == "py":
        content = re.sub(r"#.*", "", content)  # Remove Python `#` comments
        content = re.sub(r'""".*?"""', "", content, flags=re.DOTALL)  # Remove Python docstrings
    
    elif file_ext == "sql":
        content = re.sub(r"--.*", "", content)  # Remove SQL `--` comments
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)  # Remove SQL `/* */` comments
    
    elif file_ext == "json":
        content = re.sub(r'//.*', "", content)  # Remove JSON `//` comments
    
    elif file_ext == "xml":
        content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)  # Remove XML `<!-- -->` comments
    
    return content.strip()


def process_file(file_path, file_extension):
    if file_extension == "py":
        with open(file_path, 'r') as f:
            script_content = f.read()
            print(' '.join(script_content.split()[:100]))
        report = analyze_etl_script(script_content, "python", additional_questions="None")
        print(f"Generated report: {report}")
    elif file_extension == "sql":
        with open(file_path, 'r') as f:
            script_content = f.read()
        report = analyze_etl_script(script_content, "sql")
    elif file_extension == "json":
        with open(file_path, 'r') as f:
            json_content = json.load(f)
        report = analyze_etl_script(json.dumps(json_content), "json")
    elif file_extension == "xml":
        with open(file_path, 'r') as f:
            xml_content = f.read()
        report = analyze_etl_script(xml_content, "xml")
    elif file_extension == "csv":
        with open(file_path, 'r') as f:
            csv_content = f.read()
        report = analyze_etl_script(csv_content, "csv")
    else:
        return {"error": f"Unsupported file format: {file_extension}"}

    return report


def read_file_content(file_path):
    """Reads a file and removes comments/documentation to retain only executable code."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        file_ext = os.path.splitext(file_path)[1].lower()

        # Comment removal based on file type
        if file_ext == ".py":
            content = re.sub(r"#.*", "", content)  # Remove Python comments
        elif file_ext == ".sql":
            content = re.sub(r"--.*", "", content)  # Remove SQL single-line comments
            content = re.sub(r"/\*[\s\S]*?\*/", "", content)  # Remove SQL multi-line comments
        elif file_ext == ".sh":
            content = re.sub(r"#.*", "", content)  # Remove Shell script comments
        elif file_ext in {".yaml", ".yml"}:
            content = re.sub(r"#.*", "", content)  # Remove YAML comments
        elif file_ext == ".json":
            pass  # JSON does not have inline comments
        elif file_ext == ".xml":
            content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)  # Remove XML comments
        elif file_ext == ".csv":
            pass  # CSV is usually data, no comment removal needed
        elif file_ext == ".java":
            content = re.sub(r"//.*", "", content)  # Remove Java single-line comments
            content = re.sub(r"/\*[\s\S]*?\*/", "", content)  # Remove Java multi-line comments
        elif file_ext == ".ipynb":
            pass  # Jupyter notebooks are JSON-based, no comment removal
        elif file_ext == ".bat":
            content = re.sub(r"::.*", "", content)  # Remove Windows Batch comments
            content = re.sub(r"REM .*", "", content)  # Another way to remove batch comments
        elif file_ext == ".ps1":
            content = re.sub(r"#.*", "", content)  # Remove PowerShell comments
        elif file_ext == ".pl":
            content = re.sub(r"#.*", "", content)  # Remove Perl comments
        elif file_ext == ".rb":
            content = re.sub(r"#.*", "", content)  # Remove Ruby comments
        elif file_ext == ".php":
            content = re.sub(r"//.*", "", content)  # Remove PHP single-line comments
            content = re.sub(r"/\*[\s\S]*?\*/", "", content)  # Remove PHP multi-line comments
        elif file_ext == ".r":
            content = re.sub(r"#.*", "", content)  # Remove R script comments
        elif file_ext == ".scala":
            content = re.sub(r"//.*", "", content)  # Remove Scala single-line comments
            content = re.sub(r"/\*[\s\S]*?\*/", "", content)  # Remove Scala multi-line comments
        elif file_ext == ".go":
            content = re.sub(r"//.*", "", content)  # Remove Go single-line comments
            content = re.sub(r"/\*[\s\S]*?\*/", "", content)  # Remove Go multi-line comments
        elif file_ext == ".c":
            content = re.sub(r"//.*", "", content)  # Remove C single-line comments
            content = re.sub(r"/\*[\s\S]*?\*/", "", content)  # Remove C multi-line comments
        elif file_ext == ".cpp":
            content = re.sub(r"//.*", "", content)  # Remove C++ single-line comments
            content = re.sub(r"/\*[\s\S]*?\*/", "", content)  # Remove C++ multi-line comments
        elif file_ext == ".ts":
            content = re.sub(r"//.*", "", content)  # Remove TypeScript single-line comments
            content = re.sub(r"/\*[\s\S]*?\*/", "", content)  # Remove TypeScript multi-line comments
        elif file_ext == ".js":
            content = re.sub(r"//.*", "", content)  # Remove JavaScript single-line comments
            content = re.sub(r"/\*[\s\S]*?\*/", "", content)  # Remove JavaScript multi-line comments

        print(f"[INFO] Processed file: {file_path} (Cleaned length: {len(content)} chars)")
        return content.strip()

    except Exception as e:
        print(f"[ERROR] Failed to read {file_path}: {e}")
        return ""
    


def traverse_directory(root_dir, allowed_extensions=None):
    """
    Recursively fetch valid ETL script files inside a directory.

    - Only allows files with specific extensions.
    - Skips system, hidden, and non-UTF-8 files.

    Args:
        root_dir (str): Directory to scan.
        allowed_extensions (set): Allowed file extensions.
        
    Returns:
        list: List of valid file paths.
    """
    if allowed_extensions is None:
        allowed_extensions = {
            ".py", ".sql", ".sh", ".txt", ".yaml", ".yml", ".json", ".xml",
            ".csv", ".java", ".ipynb", ".bat", ".ps1", ".pl", ".rb", ".php",
            ".r", ".scala", ".go", ".c", ".cpp", ".ts", ".js"
        }  # Full list of script & config extensions

    all_files = []

    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            file_path = os.path.join(dirpath, file)

            # Skip hidden/system files
            if file.startswith("."):
                continue  

            # Only allow explicitly listed file extensions
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext not in allowed_extensions:
                continue  

            # Check if file is UTF-8 encoded before adding
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    _ = f.read()  # Validate UTF-8 encoding
                all_files.append(file_path)
            except UnicodeDecodeError:
                continue  

    return all_files


def split_large_script(script, chunk_size=50000):
    """Splits a large script into smaller chunks to avoid API input limits."""
    return [script[i:i+chunk_size] for i in range(0, len(script), chunk_size)]

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


#New Modified code -- additional question and json output also added
def analyze_etl_script(script_content, additional_questions=None):
    """Sends the cleaned script to GenAI for audit analysis and extracts structured JSON output."""
    
    print("Entering analyze_etl_script() function...")
    print(f"Script Content (first 100 chars): {script_content[:100]}")

    prompt = f"""
    You are an ETL audit expert. Analyze the following ETL script for compliance.
    
    Ignore comments and documentation. Only check executable code.
    
    {script_content}
    **Check for compliance on the following aspects:**
    1. **Auditability** (Start/End timestamps, row counts, logs)
    2. **Reconcilability** (Data movement checks, transformations)
    3. **Restartability** (Resumes from failure?)
    4. **Exception Handling** (Errors, alerts)
    5. **Script Contains Only Comments/Readme?** [YES/NO]
    6. **Follows Best Practices?** [YES/NO]

    **For each category, return structured JSON with:**
    - **result** → (YES, NO, PARTIAL)
    - **evidence** → Provide a **detailed and technical** justification with:
      - Observations from the script.
      - Technical improvements needed.
      - Specific lines or code patterns that should be improved.
    """

    # If additional questions are provided, add them
    if additional_questions:
        prompt += f"\n\nAdditionally, answer the following questions:\n{additional_questions}"

    # Enforce structured JSON format
    prompt += """
    
    **Provide structured JSON output at the end in this format and in evidence section add all that have given in the response i.e, all the technical terms and area of improvement:**
    'so i am using the below to extract output so be serious about generating this output'
    structured_match = re.search(r"```structured-results\n({.*?})\n```", audit_report, re.DOTALL)

    ```structured-results
    {
      "Auditability": {"result": "YES/NO", "evidence": "Detailed analysis..."},
      "Reconcilability": {"result": "YES/NO", "evidence": "Detailed analysis..."},
      "Restartability": {"result": "YES/NO", "evidence": "Detailed analysis..."},
      "Exception Handling": {"result": "PARTIAL/YES/NO", "evidence": "Detailed analysis..."},
      "Script Contains Only Comments/Readme": {"result": "YES/NO", "evidence": "Reasoning..."},
      "Follows Best Practices": {"result": "YES/NO", "evidence": "Detailed analysis..."}
    }
    ```
    
     **If additional questions were asked, format them as follows (otherwise, do not include this section):**
    ```structured-results
    {
      ...
     "Additional Questions":{
         "Your question here": {"result": "YES/NO", "evidence": "Detailed analysis..."},
         } 
    }
    ```
    **DO NOT** include any extra text outside of the JSON output.
    """

    print("Generated Prompt:")
    print(prompt[:300])  # Print only the first 300 characters for debugging

    try:
        completion = call_genai_api(prompt)  # Call API with retry logic
        print("Received response from GenAI model.")

        audit_report = ""
        for chunk in completion:
            # if chunk["choices"][0]["delta"].get("content") is not None:
            #     print(chunk["choices"][0]["delta"]["content"], end="")
            #     audit_report += chunk["choices"][0]["delta"]["content"]
            if chunk.choices[0].delta.content is not None:
              print(chunk.choices[0].delta.content, end="")
              audit_report += chunk.choices[0].delta.content
                

        # Extract structured JSON using regex
        structured_match = re.search(r"```structured-results\n({.*?})\n```", audit_report, re.DOTALL)

        if structured_match:
            structured_json_str = structured_match.group(1)
            try:
                structured_results = json.loads(structured_json_str)
                return structured_results  # Return structured JSON
            except json.JSONDecodeError:
                print("[ERROR] Failed to parse structured JSON.")
                return {"error": "Failed to parse structured JSON."}

        print("[WARNING] No structured JSON found! Returning full text instead.")
        return {"error": "AI did not return structured JSON", "raw_text": audit_report}

    except Exception as e:
        print("ERROR OCCURRED in analyze_etl_script:", str(e))
        return {"error": str(e) + "\n\nPlease check the input and try again."}






@etl_upload_bp.route("/upload", methods=["POST"])
def upload_file():
    """Handles file upload and extracts ZIP contents recursively."""
    
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file provided"}), 400

    file_ext = file.filename.split(".")[-1].lower()
    unique_folder = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()))
    os.makedirs(unique_folder, exist_ok=True)

    file_path = os.path.join(unique_folder, file.filename)
    file.save(file_path)  # Save uploaded file

    extracted_files = []

    if file_ext == "zip":
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(unique_folder)
        
        extracted_files = traverse_directory(unique_folder)

        if not extracted_files:
            return jsonify({"error": "ZIP extracted but contains no valid files"}), 400
    else:
        extracted_files = [file_path]

    return jsonify({
        "message": "Files processed successfully.",
        "latest_files": extracted_files
    }), 200



#Modified code 4 -- getting strucutred json output

audit_results_cache = {}
@etl_upload_bp.route("/audit", methods=["POST"])
def audit_etl():
    """Handles ETL audit for uploaded files and returns structured JSON output."""
    data = request.json
    latest_files = data.get("latest_files", [])
    test_mode = data.get("test_mode", False)
    additional_questions = data.get("additional_questions", None)  # Capture additional questions

    if not latest_files:
        print("[ERROR] No files provided for audit.")
        return jsonify({"error": "No files provided for audit"}), 400

    combined_script_content = ""
    
    for file_path in latest_files:
        if not os.path.exists(file_path):
            print(f"[WARNING] Skipping missing file: {file_path}")
            continue

        script_content = read_file_content(file_path)

        if script_content:
            combined_script_content += f"\n### File: {file_path} ###\n{script_content}\n"

    if not combined_script_content.strip():
        print("[ERROR] No valid files to process.")
        return jsonify({"error": "No valid files to process"}), 400

    # Split script if too large
    script_chunks = split_large_script(combined_script_content)

    # If test mode is enabled, return a small chunk to check API response
    if test_mode:
        test_prompt = f"Test this script for ETL compliance:\n\n{script_chunks[0]}"
        return jsonify({"test_prompt": test_prompt}), 200

    full_report = []
    
    
    # // we need to sumerise it which code is not implemented till now we can do 
    for chunk in script_chunks:
        audit_result = analyze_etl_script(chunk, additional_questions)
        
        if "error" in audit_result:
            print("[ERROR] API call failed:", audit_result["error"])
            return jsonify({"error": "Failed to analyze script"}), 500
        
        
        full_report.append(audit_result)  # Append structured JSON

    # Merge multiple JSON results
    final_report = {
        "Auditability": {"result": [], "evidence": []},
        "Reconcilability": {"result": [], "evidence": []},
        "Restartability": {"result": [], "evidence": []},
        "Exception Handling": {"result": [], "evidence": []},
        "Script Contains Only Comments/Readme": {"result": [], "evidence": []},
        "Follows Best Practices": {"result": [], "evidence": []},
        "Additional Questions": {}  # Stores questions as key-value pairs (No result/evidence structure)
    }

    # for report in full_report:
    #     for key in report:
    #         if key == "Additional Questions":
    #             final_report[key].update(report[key])  # Directly store key-value answers
    #         elif key in final_report:
    #             final_report[key]["result"].append(report[key].get("result", "N/A"))
    #             final_report[key]["evidence"].append(report[key].get("evidence", "N/A"))
    #         else:
    #             print(f"⚠️ Warning: Unexpected key '{key}' in report.")
    
    for report in full_report:
      for key in report:
        if key == "Additional Questions":
            # Ensure each question follows structured result/evidence format
            for question, details in report[key].items():
                if question not in final_report[key]:  # First time seeing this question
                    final_report[key][question] = {"result": [], "evidence": []}
                
                final_report[key][question]["result"].append(details.get("result", "N/A"))
                final_report[key][question]["evidence"].append(details.get("evidence", "N/A"))

        elif key in final_report:
            final_report[key]["result"].append(report[key].get("result", "N/A"))
            final_report[key]["evidence"].append(report[key].get("evidence", "N/A"))
        else:
            print(f"⚠️ Warning: Unexpected key '{key}' in report.")

    print("✅ Final Report:", final_report)
    audit_results_cache["final"] = final_report  

    return jsonify({"structured_audit_report": final_report}), 200


# #Modified code 3 -- getting strucutred json output
# @etl_upload_bp.route("/audit", methods=["POST"])
# def audit_etl():
#     """Handles ETL audit for uploaded files and returns structured JSON output."""
#     data = request.json
#     latest_files = data.get("latest_files", [])
#     test_mode = data.get("test_mode", False)
#     additional_questions = data.get("additional_questions", None)  # Capture additional questions

#     if not latest_files:
#         print("[ERROR] No files provided for audit.")
#         return jsonify({"error": "No files provided for audit"}), 400

#     combined_script_content = ""
    
#     for file_path in latest_files:
#         if not os.path.exists(file_path):
#             print(f"[WARNING] Skipping missing file: {file_path}")
#             continue

#         script_content = read_file_content(file_path)

#         if script_content:
#             combined_script_content += f"\n### File: {file_path} ###\n{script_content}\n"

#     if not combined_script_content.strip():
#         print("[ERROR] No valid files to process.")
#         return jsonify({"error": "No valid files to process"}), 400

#     # Split script if too large
#     script_chunks = split_large_script(combined_script_content)

#     # If test mode is enabled, return a small chunk to check API response
#     if test_mode:
#         test_prompt = f"Test this script for ETL compliance:\n\n{script_chunks[0]}"
#         return jsonify({"test_prompt": test_prompt}), 200

#     full_report = []
    
#     for chunk in script_chunks:
#         audit_result = analyze_etl_script(chunk, additional_questions)
        
#         if "error" in audit_result:
#             print("[ERROR] API call failed:", audit_result["error"])
#             return jsonify({"error": "Failed to analyze script"}), 500
        
#         full_report.append(audit_result)  # Append structured JSON

#     # audit_results_cache["latest"] = full_report
    
#     # Merge multiple JSON results
#     final_report = {
#         "Auditability": {"result": [], "evidence": []},
#         "Reconcilability": {"result": [], "evidence": []},
#         "Restartability": {"result": [], "evidence": []},
#         "Exception Handling": {"result": [], "evidence": []},
#         "Script Contains Only Comments/Readme": {"result": [], "evidence": []},
#         "Follows Best Practices": {"result": [], "evidence": []},
#         "Additional Questions": {}  # Placeholder for additional questions
#     }

#     for report in full_report:
#         for key in final_report.keys():
#             if key in report:
#                 final_report[key]["result"].append(report[key]["result"])
#                 final_report[key]["evidence"].append(report[key]["evidence"])

#         # Merge additional questions
#         if "Additional Questions" in report:
#             final_report["Additional Questions"].update(report["Additional Questions"])
#     print("final_report", final_report)
#     audit_results_cache["final"] = final_report  
#     return jsonify({"structured_audit_report": final_report}), 200




def generate_csv_report(audit_results, output_path):
    """Generates a well-formatted CSV report for ETL audit results."""
    
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            # **Header Section**
            writer.writerow(["ETL Audit Report"])
            writer.writerow(["Timestamp:", audit_results.get("timestamp", "N/A")])
            writer.writerow(["Audit Done By:", audit_results.get("auditor", "Automated System")])
            writer.writerow([])  # Empty row for spacing

            # **Table Headers**
            writer.writerow(["Category", "Status", "Key Findings"])

            # **Handle standard audit fields**
            standard_categories = [
                "Auditability", "Reconcilability", "Restartability", 
                "Exception Handling", "Script Contains Only Comments/Readme", "Follows Best Practices"
            ]

            for category in standard_categories:
                if category in audit_results:
                    details = audit_results[category]
                    status = ", ".join(details.get("result", ["N/A"]))  # Convert list to string
                    findings = "; ".join(details.get("evidence", ["No evidence provided"]))
                    writer.writerow([category, status, findings])

            # **Handle Additional Questions (if any)**
            additional_questions = audit_results.get("Additional Questions", {})
            if additional_questions:
                writer.writerow([])  # Empty row
                writer.writerow(["Additional Questions"])
                for question, response in additional_questions.items():
                    writer.writerow([question, response])

        print(f"[INFO] CSV report successfully generated: {output_path}")

    except Exception as e:
        print(f"[ERROR] Failed to generate CSV: {str(e)}")




@etl_upload_bp.route("/download_csv", methods=["GET"])
def download_cached_csv():
    """Downloads the last audit CSV report with a unique timestamp in the filename."""
    if "final" not in audit_results_cache:
        return jsonify({"error": "No audit data available"}), 400

    final_audit_data = audit_results_cache["final"]  # Use the final merged report

    folder_name = "etl_audit"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  
    safe_folder_name = folder_name.replace(" ", "_").replace("/", "_")  

    csv_filename = f"{safe_folder_name}_audit_{timestamp}.csv"
    csv_path = os.path.join(OUTPUT_FOLDER, csv_filename)

    # Generate CSV report
    generate_csv_report(final_audit_data, csv_path)  

    # 🛠 **Check if the file exists before sending**
    # if not os.path.exists(csv_path):
    #     print(f"[ERROR] CSV file was not created: {csv_path}")  
    #     return jsonify({"error": "Failed to generate report"}), 500

    print(f"[INFO] Sending file: {csv_path}")
    return send_file(csv_path, as_attachment=True)

