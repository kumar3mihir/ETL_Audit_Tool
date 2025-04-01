// /src/pages/EtlAudit.tsx

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import FileUploadForm from "../components/FileUploadForm";
import ProgressBar from "../components/ProgressBar";

const EtlAuditPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [additionalQuestions, setAdditionalQuestions] = useState<{ [key: string]: string }>({
    "Checklist for Audit": ""
  });

  const navigate = useNavigate();

  useEffect(() => {
    if (file) {
      setProgress(0);
      setErrorMessage(null);
    }
  }, [file]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files ? e.target.files[0] : null);
  };

  const handleInputChange = (key: string, value: string) => {
    setAdditionalQuestions((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setErrorMessage("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    Object.entries(additionalQuestions).forEach(([key, value]) => {
      formData.append(key, value);
    });

    try {
      setProgress(20);
      setErrorMessage(null);

      console.log("🚀 Uploading file...");
      const uploadRes = await axios.post("http://127.0.0.1:5000/etl/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      if (!uploadRes.data.latest_files) {
        setErrorMessage("Upload failed: No files found in response.");
        return;
      }

      setProgress(50);

      console.log("🚀 Starting audit...");
      const auditRes = await axios.post("http://127.0.0.1:5000/etl/audit", {
        latest_files: uploadRes.data.latest_files,
        additional_data: additionalQuestions,
        test_mode: false,
      });

      if (!auditRes.data.structured_audit_report) {
        setErrorMessage("Audit failed: No audit results found.");
        return;
      }

      setProgress(100);
      navigate("/results", { state: { auditResults: auditRes.data.structured_audit_report } });
    } catch (error) {
      console.error("❌ Error during upload/audit:", error);
      setErrorMessage("An error occurred. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center py-12">
      <div className="w-full max-w-2xl space-y-8">
        {errorMessage && <p className="text-red-500">{errorMessage}</p>}
        <FileUploadForm
          onFileChange={handleFileChange}
          onSubmit={handleSubmit}
          file={file}
          additionalQuestions={additionalQuestions}
          onInputChange={handleInputChange}
        />
        {progress > 0 && progress < 100 && <ProgressBar progress={progress} />}
      </div>
    </div>
  );
};

export default EtlAuditPage;



// import React, { useState, useEffect } from "react";
// import { useNavigate } from "react-router-dom";
// import axios from "axios";
// import FileUploadForm from "../components/FileUploadForm";
// import ProgressBar from "../components/ProgressBar";

// const EtlAuditPage: React.FC = () => {
//   const [file, setFile] = useState<File | null>(null);
//   const [additionalQuestions, setAdditionalQuestions] = useState<string>("");
//   const [progress, setProgress] = useState<number>(0);
//   const [errorMessage, setErrorMessage] = useState<string | null>(null);
//   const navigate = useNavigate(); // ✅ Used for redirection

//   // Reset progress when a new file is selected
//   useEffect(() => {
//     if (file) {
//       setProgress(0);
//       setErrorMessage(null);
//     }
//   }, [file]);

//   // Handle file selection
//   const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
//     setFile(e.target.files ? e.target.files[0] : null);
//   };

//   // Handle text input change
//   const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
//     setAdditionalQuestions(e.target.value);
//   };

//   // Handle file upload and audit
//   const handleSubmit = async (e: React.FormEvent) => {
//     e.preventDefault();
//     if (!file) {
//       setErrorMessage("Please select a file to upload.");
//       return;
//     }

//     const formData = new FormData();
//     formData.append("file", file);

//     try {
//       setProgress(20); // Start progress
//       setErrorMessage(null);

//       console.log("🚀 Uploading file...");
//       const uploadRes = await axios.post("http://127.0.0.1:5000/etl/upload", formData, {
//         headers: { "Content-Type": "multipart/form-data" },
//       });

//       console.log("✅ Upload Response:", uploadRes.data);
//       if (!uploadRes.data.latest_files) {
//         setErrorMessage("Upload failed: No files found in response.");
//         return;
//       }

//       setProgress(50); // Midway progress

//       console.log("🚀 Starting audit...");
//       const auditRes = await axios.post("http://127.0.0.1:5000/etl/audit", {
//         latest_files: uploadRes.data.latest_files, // ✅ Correct key
//         additional_questions: additionalQuestions,
//         test_mode: false,
//       });

//       console.log("✅ Audit Response:", auditRes.data);

//       if (!auditRes.data.structured_audit_report) {
//         setErrorMessage("Audit failed: No structured audit report found.");
//         return;
//       }

//       setProgress(100); // Completed

//       // Redirect to Results page with audit data
//       navigate("/results", { state: { auditResults: auditRes.data.structured_audit_report } });
//     } catch (error) {
//       console.error("❌ Error during upload/audit:", error);
//       setErrorMessage("An error occurred. Please try again.");
//     }
//   };

//   return (
//     <div className="min-h-screen bg-gray-100 flex items-center justify-center py-12">
//       <div className="w-full max-w-2xl space-y-8">
//         {errorMessage && <p className="text-red-500">{errorMessage}</p>}

//         <FileUploadForm
//           onFileChange={handleFileChange}
//           onSubmit={handleSubmit}
//           file={file}
//           additionalQuestions={additionalQuestions}
//           onInputChange={handleInputChange}
//         />

//         {progress > 0 && progress < 100 && <ProgressBar progress={progress} />}
//       </div>
//     </div>
//   );
// };

// export default EtlAuditPage;
