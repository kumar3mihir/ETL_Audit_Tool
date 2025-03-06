import React, { useState } from "react";
import axios from "axios";

function EtlUploadForm() {
  const [file, setFile] = useState(null);
  const [additionalQuestions, setAdditionalQuestions] = useState("");
  const [progress, setProgress] = useState(0);
  const [auditResult, setAuditResult] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleInputChange = (e) => {
    setAdditionalQuestions(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append("file", file);
    formData.append("additional_questions", additionalQuestions);

    try {
      // Upload the file and send the request
      const uploadRes = await axios.post("http://localhost:5000/etl/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      if (uploadRes.data.message === "File uploaded successfully.") {
        // After upload, send the file for auditing
        const auditRes = await axios.post(
          "http://localhost:5000/etl/audit",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
            onUploadProgress: (progressEvent) => {
              const percentCompleted = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
              setProgress(percentCompleted);
            },
          }
        );

        setAuditResult(auditRes.data.audit_report);
      }
    } catch (error) {
      console.error("Error during upload or audit:", error);
    }
  };

  const handleDownload = async () => {
    try {
      const downloadRes = await axios.get(
        "http://localhost:5000/etl/download",
        { responseType: "blob" }
      );
      const file = new Blob([downloadRes.data], { type: "text/csv" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(file);
      link.download = "audit_report.csv";
      link.click();
    } catch (error) {
      console.error("Error downloading CSV:", error);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <label>
          Upload ETL Script:
          <input type="file" onChange={handleFileChange} />
        </label>
        <br />
        <label>
          Additional Questions:
          <textarea
            value={additionalQuestions}
            onChange={handleInputChange}
            placeholder="Enter any custom audit questions"
          />
        </label>
        <br />
        <button type="submit">Submit</button>
      </form>

      {progress > 0 && progress < 100 && (
        <div>
          <h4>Processing... {progress}%</h4>
          <progress value={progress} max="100" />
        </div>
      )}

      {auditResult && (
        <div>
          <h3>Audit Report:</h3>
          <pre>{JSON.stringify(auditResult, null, 2)}</pre>
          <button onClick={handleDownload}>Download CSV Report</button>
        </div>
      )}
    </div>
  );
}

export default EtlUploadForm;
