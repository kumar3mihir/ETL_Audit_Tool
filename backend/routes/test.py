import os
import csv

# Define output folder
OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def generate_csv_report(audit_results, output_filename="etl_audit_report.csv", test_mode=False):
    """Generates a well-formatted CSV report for ETL audit results."""
    
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    # Open CSV file for writing
    with open(output_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)

        # **Header Section**
        writer.writerow(["ETL Audit Report"])
        writer.writerow(["Folder Name:", audit_results.get("folder_name", "N/A")])
        writer.writerow(["Timestamp:", audit_results.get("timestamp", "N/A")])
        writer.writerow(["Audit Done By:", audit_results.get("auditor", "Automated System")])
        writer.writerow([])  # Empty row for spacing

        # **Table Headers**
        writer.writerow(["Category", "Status", "Key Findings"])

        # **Adding Audit Data**
        all_audit_sections = audit_results.get("compliance_analysis", {}) | audit_results.get("code_quality_checks", {})

        for category, details in all_audit_sections.items():
            status = details.get("result", "N/A")  # Fix: Used `result` key properly
            findings = details.get("evidence", "No findings available")

            writer.writerow([category, status, findings])

    # **Test Mode: Print Output Instead of Saving**
    if test_mode:
        with open(output_path, "r", encoding="utf-8") as f:
            print("[TEST MODE] CSV content:")
            print(f.read())
        return "Test mode completed successfully."

    print(f"[INFO] CSV report generated: {output_path}")
    return output_path


# **Test Data**
test_data = {
    "compliance_analysis": {
        "auditability": {
            "result": "NO",
            "evidence": "No timestamps, row counts, or logging mechanisms found in executable code. Report generation lacks audit trails."
        },
        "reconcilability": {
            "result": "NO", 
            "evidence": "No data validation checks, checksums, or reconciliation logic between input data and generated reports."
        },
        "restartability": {
            "result": "NO",
            "evidence": "No checkpoints, job state tracking, or failure recovery mechanisms. Processes appear to run atomically."
        },
        "exception_handling": {
            "result": "NO",
            "evidence": "No try/except blocks, error logging, or alerting mechanisms visible in code snippets."
        }
    },
    "code_quality_checks": {
        "comments_only": {
            "result": "NO",
            "evidence": "Contains executable PDF/Excel generation and Flask route handlers"
        },
        "best_practices": {
            "result": "NO",
            "evidence": "Missing input validation, error handling, and resource cleanup (e.g., no buffer.close()). Directly returning BytesIO buffer without stream management."
        }
    }
}

# **Run Function in Test Mode**
generate_csv_report(test_data, test_mode=False)

# **Run Function Normally (Saves CSV File)**
generate_csv_report(test_data)
