import React from "react";

interface AuditResultProps {
  auditReport: string | null;
  onDownload: () => void;
}

const AuditResult: React.FC<AuditResultProps> = ({ auditReport, onDownload }) => {
  return (
    <div className="max-w-xl mx-auto p-6 bg-white shadow-lg rounded-lg">
      {auditReport ? (
        <>
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">
            Audit Report
          </h2>
          <pre className="bg-gray-100 p-4 rounded-md text-gray-700 mb-4">{auditReport}</pre>
          <button
            onClick={onDownload}
            className="w-full py-2 px-4 bg-green-600 text-white rounded-md hover:bg-green-700 transition"
          >
            Download Audit Report (CSV)
          </button>
        </>
      ) : (
        <p className="text-gray-600">Your audit result will appear here.</p>
      )}
    </div>
  );
};

export default AuditResult;
