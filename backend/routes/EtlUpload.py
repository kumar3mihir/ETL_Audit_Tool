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
from werkzeug.utils import secure_filename
import re
import time
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import openai
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
ALLOWED_FILE_EXTENSIONS = [".py", ".sql", ".sh", ".txt", ".yaml", ".yml", ".json", ".xml",
            ".csv", ".java", ".ipynb", ".bat", ".ps1", ".pl", ".rb", ".php",
            ".r", ".scala", ".go", ".c", ".cpp", ".ts", ".js"]
OUTPUT_FOLDER = "/Users/mihirkumarmallick/Desktop/access_parent/project/output"

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXTRACTED_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Global variable to store audit results
audit_results_cache = {}

def is_valid_etl_file(file_path):
    """Check if the file is an ETL script based on its extension."""
    _, extension = os.path.splitext(file_path)
    return extension.lower() in ALLOWED_FILE_EXTENSIONS

def validate_json(json_file):
    """Try to parse JSON file to check if it is valid."""
    try:
        with open(json_file, 'r') as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, IOError):
        return False

def validate_xml(xml_file):
    """Try to parse XML file to check if it is valid."""
    try:
        with open(xml_file, 'r') as f:
            ET.parse(f)
        return True
    except (ET.ParseError, IOError):
        return False

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
        }

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

def split_large_script(script, chunk_size=8000):
    """
    Splits a large script into smaller chunks while trying to maintain code integrity.
    This uses a simple text-based approach rather than parsing functions.
    
    Args:
        script (str): The script content to split
        chunk_size (int): Maximum size of each chunk in characters
        
    Returns:
        list: List of script chunks
    """
    # If script is small enough, return as is
    if len(script) <= chunk_size:
        return [script]
    
    chunks = []
    start_idx = 0
    
    while start_idx < len(script):
        # Get a chunk of approximately chunk_size
        end_idx = min(start_idx + chunk_size, len(script))
        
        # If we're not at the end, try to find a good breaking point
        if end_idx < len(script):
            # Look for good breaking points: newlines followed by non-indented lines
            # This helps preserve code blocks
            for i in range(end_idx, max(start_idx, end_idx - 200), -1):
                if i < len(script) and script[i] == '\n':
                    # Check if the next line is non-indented (likely a new block)
                    if i+1 < len(script) and not script[i+1].isspace():
                        end_idx = i + 1
                        break
        
        current_chunk = script[start_idx:end_idx]
        chunks.append(current_chunk)
        start_idx = end_idx
    
    return chunks

def merge_audit_results(results_list):
    """
    Merges audit results from multiple chunks of the same file.
    
    Args:
        results_list (list): List of audit results from different chunks
        
    Returns:
        dict: Merged audit results
    """
    if not results_list:
        return {}
    
    # Use the first result as a base
    merged_results = results_list[0]
    
    # For simplicity, we'll return the most conservative result (fail over pass)
    # and concatenate the evidence
    if len(results_list) > 1:
        for result in results_list[1:]:
            if not result:
                continue
                
            for file_audit in result:
                # Find matching file in merged results
                matching_file = None
                for merged_file in merged_results:
                    if merged_file.get("File Name Full Path") == file_audit.get("File Name Full Path"):
                        matching_file = merged_file
                        break
                
                if not matching_file:
                    # If no match found, add the whole file audit
                    merged_results.append(file_audit)
                    continue
                
                # Merge audit results for the matching file
                for audit_result in file_audit.get("Audit Results", []):
                    audit_type = audit_result.get("ETL Audit Type")
                    
                    # Find matching audit type in merged results
                    matching_audit = None
                    for merged_audit in matching_file.get("Audit Results", []):
                        if merged_audit.get("ETL Audit Type") == audit_type:
                            matching_audit = merged_audit
                            break
                    
                    if not matching_audit:
                        # If no match found, add the whole audit result
                        matching_file["Audit Results"].append(audit_result)
                        continue
                    
                    # If either chunk resulted in a "Fail", the merged result is "Fail"
                    if audit_result.get("Audit Result") == "Fail":
                        matching_audit["Audit Result"] = "Fail"
                    
                    # Concatenate evidence
                    if "Audit Details/Evidence" in audit_result and "Detailed Analysis" in audit_result["Audit Details/Evidence"]:
                        current_evidence = matching_audit.get("Audit Details/Evidence", {}).get("Detailed Analysis", "")
                        new_evidence = audit_result["Audit Details/Evidence"]["Detailed Analysis"]
                        
                        # Avoid duplication
                        if new_evidence not in current_evidence:
                            matching_audit["Audit Details/Evidence"] = {
                                "Detailed Analysis": f"{current_evidence}\n\nAdditional evidence from chunk analysis:\n{new_evidence}"
                            }
    
    return merged_results

# Configure Nvidia API
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

def valid_etl_code_files(file_path):
    """
    Checks if the given file path contains valid executable ETL code files.

    Args:
        file_path (str): Path to the file or directory.

    Returns:
        bool: True if valid ETL code files are present, False otherwise.
    """
    allowed_extensions = {".py", ".sql", ".sh", ".json", ".xml", ".csv", ".java", ".js", ".ts", ".yaml", ".yml"}
    
    if os.path.isfile(file_path):
        _, extension = os.path.splitext(file_path)
        return extension.lower() in allowed_extensions

    elif os.path.isdir(file_path):
        for root, _, files in os.walk(file_path):
            for file in files:
                _, extension = os.path.splitext(file)
                if extension.lower() in allowed_extensions:
                    return True
    return False

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

# Define the prompt template with placeholders
prompt_template = """
You are an ETL Audit Expert specializing in compliance, data governance, and script validation, including checking coding standards.  
Your task is to analyze the given ETL scripts and validate them against the provided checklist.

---

### *Checklist for Validation:*  
{additional_questions}

### *Files and Code Content:*  
Below are the file paths and their respective code content:

{file_name} {script_content}


---

### *Validation Criteria:*  
If the checklist includes the following keywords: **auditability**, **reconcilability**, **restartability**, **exception handling**,  
analyze each script for compliance with these aspects:

1. **Auditability**: Check for start/end timestamps, row counts, and logs.  
2. **Reconcilability**: Ensure the ETL script includes data reconcilability checks.  
3. **Restartability**: Verify if the script can resume from the point of failure.  
4. **Exception Handling**: Assess error handling, alerts, and notifications.

---

### *Output Requirements:*  
For each file, return structured JSON with:  
- **File Name Full Path**: The full path of the file being analyzed.  
- **Audit Results**: A list of results for each validation category.  
    - **ETL Audit Type**: (Auditability, Reconcilability, Restartability, Exception Handling)  
    - **Audit Result**: (Pass/Fail)  
    - **Audit Details/Evidence**: Provide a concise and detailed justification.  

**Provide structured output at the end in this format:**
[
                {{
                        "File Name Full Path": "{file_name}",
                        "Audit Results": [
                                {{
                                        "ETL Audit Type": "Auditability",
                                        "Audit Result": "Pass/Fail",
                                        "Audit Details/Evidence": {{
                                                "Detailed Analysis": "Explain in detail how auditability is implemented or not and what it's lacking."
                                        }}
                                }},
                                {{
                                        "ETL Audit Type": "Reconcilability",
                                        "Audit Result": "Pass/Fail",
                                        "Audit Details/Evidence": {{
                                                "Detailed Analysis": "Explain in detail how reconcilability is implemented or not and what it's lacking."
                                        }}
                                }},
                                {{
                                        "ETL Audit Type": "Restartability",
                                        "Audit Result": "Pass/Fail",
                                        "Audit Details/Evidence": {{
                                                "Detailed Analysis": "Explain in detail how restartability is implemented or not and what it's lacking."
                                        }}
                                }},
                                {{
                                        "ETL Audit Type": "Exception Handling",
                                        "Audit Result": "Pass/Fail",
                                        "Audit Details/Evidence": {{
                                                "Detailed Analysis": "Explain in detail how exception handling is implemented or not and what it's lacking."
                                        }}
                                }}
                        ]
                }}
        ]
---

### *Strict Rules:*  
1. **No Extra Text**: Do not include any text outside the structured JSON output.  
2. **Structured Format**: Ensure the JSON output strictly adheres to the format provided above.  
3. **Detailed Analysis**: Provide clear and concise explanations for each audit type.  
4. **No Assumptions**: Base your analysis solely on the provided script content.  
5. **Error-Free JSON**: Ensure the JSON is syntactically correct and parsable.  
6. **Comprehensive Coverage**: Address all validation criteria mentioned in the checklist.  
7. **Professional Tone**: Maintain a formal and professional tone in the analysis.  
8. **Consistency**: Ensure consistent formatting and terminology throughout the output.  

---

### *Important Note:*  
This is {chunk_info}
"""

def analyze_etl_script(script_content, file_name=None, additional_questions=None):
    """
    Analyzes ETL scripts for compliance with best practices.
    Handles large scripts by splitting them into chunks and merging results.
    
    Args:
        script_content (str): The content of the ETL script to analyze
        file_name (str, optional): The name of the file being analyzed
        additional_questions (str, optional): Additional analysis questions
        
    Returns:
        dict: Analysis results in structured format
    """
    print(f"\n🔍 [DEBUG] Analyzing script: {file_name} (length: {len(script_content)} chars)")
    
    # Split large scripts into manageable chunks
    MAX_CHUNK_SIZE = 50000  # Adjust based on API limits
    chunks = split_large_script(script_content, MAX_CHUNK_SIZE)
    
    print(f"📌 [DEBUG] Number of script chunks: {len(chunks)}")
    
    all_results = []
    
    for i, chunk in enumerate(chunks):
        # Prepare chunk information for the prompt
        chunk_info = f"chunk {i+1} of {len(chunks)} for file {file_name}" if len(chunks) > 1 else f"the complete content of file {file_name}"
        
        print(f"\n📝 [DEBUG] Processing {chunk_info}")
        print(f"📜 [DEBUG] Chunk Content (First 500 chars): {chunk[:500]}")
        
        # Ensure `prompt_template` exists and has correct placeholders
        print(f"🔄 [DEBUG] Formatting prompt with template...")
        try:
            print(f"📨 [DEBUG] Formatting prompt with template...")  

            # Debug values before formatting
            print(f"📜 [DEBUG] prompt_template: {prompt_template}")  # Print the raw template
            print(f"📌 [DEBUG] script_content: {chunk[:50] if chunk else 'N/A'}")  
            print(f"📌 [DEBUG] file_name: {file_name}")  
            print(f"📌 [DEBUG] additional_questions: {additional_questions}")  
            print(f"📌 [DEBUG] chunk_info: {chunk_info}")  

            # Ensure additional_questions is a properly formatted string
            formatted_questions = "\n".join(additional_questions) if isinstance(additional_questions, list) else additional_questions

            # Format the prompt
            formatted_prompt = prompt_template.format(
                additional_questions=formatted_questions if formatted_questions else "No additional questions provided.",
                file_name=str(file_name) if file_name else "Unknown",
                script_content=str(chunk) if chunk else "N/A",
                chunk_info=str(chunk_info) if chunk_info else "No chunk info available."
            )

            print("✅ [DEBUG] Formatting successful.")
        except KeyError as ke:
            print(f"❌ [ERROR] Missing key in template: {ke}")
            return {"error": f"Missing key in template: {ke}"}
        except Exception as e:
            print(f"❌ [ERROR] Formatting error: {e}")
            return {"error": f"Formatting error: {e}"}
        print(f"📨 [DEBUG] Sending request to GenAI API...")
        
    try:
        completion = call_genai_api(formatted_prompt)  # Call API with retry logic
        
        print(f"✅ [DEBUG] API call successful, processing response...")
        
        audit_report = ""

        # Ensure API response is not empty
        if not completion:
            raise ValueError("Empty response from API.")

        for chunk_response in completion:
            # Use getattr to safely access `.choices[0].delta.content`
            content = getattr(chunk_response.choices[0].delta, "content", None)
            if content:
                print(content, end="")
                audit_report += content

        print(f"📑 [DEBUG] Raw API Response : {audit_report}")

        # # Extract structured JSON using regex
        # structured_match = re.search(r"(\[\s*\{(?:[^{}]|{[^{}]*})*\}\s*\])", audit_report, re.DOTALL)
        # # structured_match = re.search(r"(\[\s*\{[\s\S]*?\}\s*\])", audit_report, re.DOTALL)

        # if structured_match:
        #     structured_json_str = structured_match.group(0)  # Use group(0) instead of group(1)
        #     print(f"🔍 [DEBUG] Full Extracted JSON:\n{structured_json_str}")            
        #     try:
        #         structured_results = json.loads(structured_json_str)  # Ensure valid JSON parsing
        #         all_results.append(structured_results)
        #     except json.JSONDecodeError as e:
        #         print(f"❌ [ERROR] Failed to parse structured JSON: {e}")
        #         all_results.append({"error": "Failed to parse structured JSON.", "raw_text": structured_json_str})
        # else:
        #     print(f"⚠️ [WARNING] No structured JSON found in chunk {i+1}")
        #     all_results.append({"error": "AI did not return structured JSON", "raw_text": audit_report})
        # Check if structured_match is defined and matches the expected pattern
        structured_match = re.search(r"(\[\s*\{(?:[^{}]|{[^{}]*})*\}\s*\])", audit_report, re.DOTALL)

        if structured_match:
            structured_json_str = structured_match.group(0)  # Use group(0) instead of group(1)
            print("=" * 50)
            print(f"🔍 [DEBUG] Full Extracted JSON (Raw):\n{structured_json_str}")
            print("=" * 50)

        #     try:
        #         structured_results = json.loads(structured_json_str)  # Ensure valid JSON parsing
        #         print(f"✅ [DEBUG] Successfully parsed JSON. Sample output:")
        #         print(json.dumps(structured_results, indent=2))  # Pretty print JSON
        #         all_results.append(structured_results)
        #     except json.JSONDecodeError as e:
        #         print(f"❌ [ERROR] Failed to parse structured JSON: {e}")
        #         all_results.append({
        #             "error": "Failed to parse structured JSON.",
        #             "raw_text": structured_json_str
        #         })
        # else:
        #     print(f"⚠️ [WARNING] No structured JSON found in chunk {i+1}")
        #     print(f"📑 [DEBUG] Full audit_report:\n{audit_report}")
        #     all_results.append({
        #         "error": "AI did not return structured JSON",
        #         "raw_text": audit_report
        #     })
        try:
            structured_results = json.loads(audit_report)  # Direct JSON parsing
            print(f"\n✅ [DEBUG] Successfully parsed JSON. Sample output:")
            print(json.dumps(structured_results, indent=2))  # Pretty print JSON
            all_results.append(structured_results)

        except json.JSONDecodeError as e:
            print(f"\n❌ [ERROR] Failed to parse JSON: {e}")
            all_results.append({"error": "Failed to parse JSON.", "raw_text": audit_report})
        
        
        
        

    except Exception as e:
        print(f"❌ [ERROR] API call failed for chunk {i+1}: {str(e)}")
        all_results.append({"error": str(e)})
    
    print(f"\n🔄 [DEBUG] Merging {len(all_results)} audit results...")
    
    # If we processed multiple chunks, merge the results
    if len(all_results) > 1:
        merged_results = merge_audit_results(all_results)
        print(f"✅ [DEBUG] Merged results successfully.")
        return merged_results
    elif all_results:
        print(f"✅ [DEBUG] Returning single chunk result.")
        return all_results[0]
    else:
        print(f"❌ [ERROR] No results obtained from analysis.")
        return {"error": "No results were obtained from the analysis"}
    
    
@etl_upload_bp.route("/upload", methods=["POST"])
def upload_file():
    """Handles file upload and extracts ZIP contents recursively."""
    
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file provided"}), 400
    
    # Create a unique folder for this upload
    unique_id = str(uuid.uuid4())
    unique_folder = os.path.join(UPLOAD_FOLDER, unique_id)
    os.makedirs(unique_folder, exist_ok=True)

    file_ext = file.filename.split(".")[-1].lower()
    file_path = os.path.join(unique_folder, secure_filename(file.filename))
    file.save(file_path)  # Save uploaded file

    extracted_files = []

    if file_ext == "zip":
        extracted_folder = os.path.join(EXTRACTED_FOLDER, unique_id)
        os.makedirs(extracted_folder, exist_ok=True)
        
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(extracted_folder)
        
        extracted_files = traverse_directory(extracted_folder)

        if not extracted_files:
            return jsonify({"error": "ZIP extracted but contains no valid files"}), 400
    else:
        extracted_files = [file_path]

    # Convert file paths to file contents
    file_data = []
    for file_path in extracted_files:
        if is_valid_etl_file(file_path):
            content = read_file_content(file_path)
            if content:  # Only add non-empty files
                file_data.append({
                    "filename": file_path,
                    "content": content
                })

    return jsonify({
        "message": "Files processed successfully.",
        "unique_id": unique_id,
        "latest_files": file_data
    }), 200

@etl_upload_bp.route("/audit", methods=["POST"])
def audit_etl():
    """Handles ETL audit for uploaded files and returns structured JSON output."""
    print("📥 Received audit request")
    
    data = request.json
    latest_files = data.get("latest_files", [])
    test_mode = data.get("test_mode", False)
    additional_questions = data.get("additional_questions", None)

    if not latest_files:
        print("[ERROR] No files provided for audit.")
        return jsonify({"error": "No files provided for audit"}), 400

    file_metadata = []  # To store metadata for each file
    
    for file in latest_files:
        file_path = file.get("filename")
        script_content = file.get("content", "")
        file_extension = os.path.splitext(file_path)[1].lower().replace(".", "")
        script_type = detect_script_type(file_path)

        print(f"[INFO] Processing file: {file_path}, Type: {script_type}")
        
        if script_content:
            file_metadata.append({
                "file_path": file_path,
                "script_content": script_content,
                "file_extension": file_extension,
                "script_type": script_type
            })
        else:
            print(f"[WARNING] Empty content in file: {file_path}")

    if not file_metadata:
        print("[ERROR] No valid files to process.")
        return jsonify({"error": "No valid files to process"}), 400

    print(f"[INFO] {len(file_metadata)} valid files found for auditing.")
    
    # If test mode is enabled, return a small chunk to check API response
    if test_mode:
        test_file = file_metadata[0]
        test_prompt = f"Test this script for ETL compliance:\n\n{test_file['script_content'][:1000]}"
        print("[DEBUG] Test mode enabled, returning sample prompt")
        return jsonify({
            "test_mode": True, 
            "test_prompt": test_prompt,
            "file_count": len(file_metadata)
        }), 200

    full_report = []
    
    # Analyze each file
    for metadata in file_metadata:
        print(f"🔍 Auditing file: {metadata['file_path']}")
        audit_result = analyze_etl_script(
            script_content=metadata["script_content"],
            file_name=metadata["file_path"],
            additional_questions=additional_questions
        )
        
        if "error" in audit_result and not isinstance(audit_result, list):
            print(f"[ERROR] API call failed for {metadata['file_path']}: {audit_result['error']}")
            continue
        
        print(f"✅ Audit completed for {metadata['file_path']}")
        full_report.append({
            "file_path": metadata["file_path"],
            "script_type": metadata["script_type"],
            "audit_result": audit_result
        })

    if not full_report:
        print("[ERROR] No audits were successfully completed.")
        return jsonify({"error": "No audits were successfully completed"}), 500

    print("[INFO] Caching audit results for report generation.")
    # Cache the audit results for report generation
    audit_results_cache["full_report"] = full_report
    
    # Generate the final report
    final_report = generate_final_report(full_report)
    audit_results_cache["final"] = final_report
    
    print("✅ Final Report Generated")

    # Return properly formatted JSON response
    return jsonify({
        "message": "Audit completed successfully",
        "file_count": len(file_metadata),
        "processed_count": len(full_report),
        "structured_audit_report": final_report
    }), 200


def generate_final_report(full_report):
    """Formats and generates the final audit report."""
    final_report = []
    audit_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("[INFO] Generating final structured audit report.")
    
    for report in full_report:
        file_path = report["file_path"]
        script_type = report["script_type"]
        audit_result = report["audit_result"]
        
        print(f"[INFO] Processing audit results for file: {file_path}")
        
        # Process each file's audit results
        for file_audit in audit_result:
            audit_results = file_audit.get("Audit Results", [])
            
            for audit_item in audit_results:
                final_report.append({
                    "Audit Start Date & Time": audit_start_time,
                    "Audit End Date & Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "File Type": script_type,
                    "File Name Full Path": file_path,
                    "Audit Status": "Completed",
                    "ETL Audit Type": audit_item.get("ETL Audit Type", "Unknown"),
                    "Audit Result": audit_item.get("Audit Result", "N/A"),
                    "Audit Details": audit_item.get("Audit Details/Evidence", {}).get("Detailed Analysis", "N/A")
                })
    
    print("✅ Final structured audit report generated successfully.")
    return final_report



@etl_upload_bp.route("/download/csv", methods=["GET"])
def download_csv():
    """Endpoint to download audit results as CSV."""
    if "final" not in audit_results_cache:
        return jsonify({"error": "No audit report found"}), 404

    # Generate CSV file
    csv_filename = os.path.join(OUTPUT_FOLDER, f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        fieldnames = [
            "Audit Start Date & Time", "Audit End Date & Time", "File Type", 
            "File Name Full Path", "Audit Status", "ETL Audit Type", 
            "Audit Result", "Audit Details"
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in audit_results_cache["final"]:
            writer.writerow(row)
    
    return send_file(csv_filename, as_attachment=True, download_name="etl_audit_report.csv")

@etl_upload_bp.route("/download/excel", methods=["GET"])
def download_excel():
    """Endpoint to download audit results as Excel file."""
    if "final" not in audit_results_cache:
        return jsonify({"error": "No audit report found"}), 404

    # Create a workbook and add a worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "ETL Audit Report"
    
    # Add headers with styling
    headers = [
        "Audit Start Date & Time", "Audit End Date & Time", "File Type", 
        "File Name Full Path", "Audit Status", "ETL Audit Type", 
        "Audit Result", "Audit Details"
    ]
    
    # Style for headers
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    
    # Write headers with styling
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.fill = header_fill
        cell.font = header_font
    
    # Write data rows
    for row_idx, row_data in enumerate(audit_results_cache["final"], 2):
        for col_idx, header in enumerate(headers, 1):
            cell_value = row_data.get(header, "")
            cell = ws.cell(row=row_idx, column=col_idx, value=cell_value)
            
            # Add special formatting for Pass/Fail cells
            if header == "Audit Result":
                if cell_value == "Pass":
                    cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
                elif cell_value == "Fail":
                    cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
    
    # Auto-adjust column width
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        adjusted_width = min(max_length + 2, 50)  # Cap width at 50 characters
        ws.column_dimensions[column].width = adjusted_width
    
    # Save the workbook
    excel_filename = os.path.join(OUTPUT_FOLDER, f"etl_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    wb.save(excel_filename)
    
    return send_file(excel_filename, as_attachment=True, download_name="etl_audit_report.xlsx")