// /src/components/FileUpload.tsx
import React, { useState, useRef } from "react";
import { Upload, X, AlertCircle, CheckCircle, Loader } from "lucide-react";
import axios from "axios";

interface FileType {
  id: string;
  name: string;
  size: number;
  status: "pending" | "error" | "success" | "processing";
}

const FileUpload: React.FC = () => {
  const [files, setFiles] = useState<FileType[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isExtracting, setIsExtracting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFiles = Array.from(e.dataTransfer.files);
    processFiles(droppedFiles);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    processFiles(selectedFiles);
  };

  const processFiles = (selectedFiles: File[]) => {
    const validFiles = selectedFiles.filter(
      (file) =>
        file.size <= 50 * 1024 * 1024 &&
        (file.name.endsWith(".csv") || file.name.endsWith(".xlsx"))
    );

    if (files.length + validFiles.length > 10) {
      alert("Maximum 10 files allowed");
      return;
    }

    setFiles((prev) => [
      ...prev,
      ...validFiles.map((file) => ({
        id: Math.random().toString(36).slice(2, 11),
        name: file.name,
        size: file.size,
        status: "pending" as "pending",
      })),
    ]);
  };

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((file) => file.id !== id));
  };

  const handleExtract = async () => {
  setIsExtracting(true);
  setFiles((prev) => prev.map((file) => ({ ...file, status: "processing" }))); //what this line means explain

  try {
    const formData = new FormData();
    files.forEach((file) => {
      const blob = new Blob([file as any], { type: "application/octet-stream" });
      formData.append("file", blob, file.name); // Append "file" instead of "files"
    });

    // Send the formData to the correct endpoint
    const response = await axios.post("http://127.0.0.1:5001/extract_metadata", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    // Handle the response
    if (response.data.metadata) {
      setFiles((prev) =>
        prev.map((file, index) => ({
          ...file,
          status: "success",
          metadata: response.data.metadata[index], // Add metadata to the file status
        }))
      );
    } else {
      setFiles((prev) => prev.map((file) => ({ ...file, status: "error" })));
    }

  } catch (error) {
    console.error("Extraction failed", error);
    setFiles((prev) => prev.map((file) => ({ ...file, status: "error" })));
  }

  setIsExtracting(false);
};


  return (
    <div className="max-w-3xl mx-auto p-6 bg-white rounded-lg shadow-md">
      {/* Drag-and-Drop & Browse Upload */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer ${
          isDragging ? "border-blue-500 bg-blue-50" : "border-gray-300"
        }`}
      >
        <Upload className="mx-auto h-12 w-12 text-gray-400" />
        <p className="mt-4 text-sm text-gray-600">
          Drag & drop files here, or{" "}
          <span
            className="text-blue-600 hover:underline cursor-pointer"
            onClick={(e) => {
              e.stopPropagation(); // Prevents triggering the parent div
              fileInputRef.current?.click();
            }}
          >
            browse
          </span>
        </p>
        <p className="mt-2 text-xs text-gray-500">CSV or Excel files up to 50MB (Max: 10 files)</p>
        <input
          type="file"
          ref={fileInputRef}
          accept=".csv,.xlsx"
          multiple
          className="hidden"
          onChange={handleFileSelect}
        />
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-6 space-y-4">
          {files.map((file) => (
            <div
              key={file.id}
              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg shadow-sm"
            >
              <div className="flex items-center space-x-4">
                {file.status === "error" ? (
                  <AlertCircle className="text-red-500" />
                ) : file.status === "processing" ? (
                  <Loader className="animate-spin text-yellow-500" />
                ) : (
                  <CheckCircle className="text-green-500" />
                )}
                <div>
                  <p className="text-sm font-medium text-gray-900">{file.name}</p>
                  <p className="text-xs text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              </div>
              <button onClick={() => removeFile(file.id)} className="text-gray-400 hover:text-gray-500">
                <X className="h-5 w-5" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Extract Button */}
      {files.length > 0 && (
        <div className="mt-6 text-center">
          <button
            onClick={handleExtract}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 flex items-center justify-center gap-2"
          >
            {isExtracting && <Loader className="animate-spin" />} Extract Metadata
          </button>
        </div>
      )}
    </div>
  );
};

export default FileUpload;



