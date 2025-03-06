import React, { useState } from "react";
import { DatabaseConnectionForm } from "../components/DatabaseConnection";
import { useNavigate } from "react-router-dom";
import FileUpload from "../components/FileUpload"; // Import the FileUpload component

const ConnectionPage: React.FC = () => {
  const [mode, setMode] = useState<"local" | "database">("database");
  const [isConnected, setIsConnected] = useState(false);
  const navigate = useNavigate();

  const handleExtractClick = () => {
    if (isConnected) {
      navigate("/metadata");
    } else {
      alert("Please connect to the database first.");
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6 bg-white rounded-lg shadow-md">
      {/* Mode Selector */}
      <div className="flex justify-center gap-4 mb-6">
        {["database", "local"].map((type) => (
          <button
            key={type}
            onClick={() => setMode(type as "local" | "database")}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
              mode === type ? "bg-blue-600 text-white shadow-md" : "bg-gray-200 text-gray-800"
            }`}
          >
            {type === "local" ? "Upload File" : "Database"}
          </button>
        ))}
      </div>

      {mode === "local" ? (
        <div>
          {/* Integrate FileUpload component here */}
          <FileUpload />

          {/* Buttons */}
          <div className="flex justify-center mt-6">
            <button
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500"
              onClick={handleExtractClick}
            >
              Extract
            </button>
          </div>
        </div>
      ) : (
        <div>
          {/* Database Connection Form */}
          {isConnected ? (
            <div className="bg-white p-6 rounded-lg shadow">
              <p>Connected to Database</p>
            </div>
          ) : (
            <DatabaseConnectionForm />
          )}
        </div>
      )}
    </div>
  );
};

export default ConnectionPage;
