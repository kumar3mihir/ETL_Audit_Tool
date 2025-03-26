import React from "react";

const MetadataExtraction = () => {
  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold text-center mb-6">Database Metadata Extraction</h1>
      
      {/* Overview Section */}
      <div className="bg-white p-6 rounded-xl shadow-md mb-6">
        <h2 className="text-xl font-semibold mb-4">Overview</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-gray-600 text-sm">Tables Count:</label>
            <input
              type="text"
              placeholder=""
              className="w-full p-2 border rounded-lg bg-gray-100"
              disabled
            />
          </div>
          <div>
            <label className="block text-gray-600 text-sm">Purpose & Summary:</label>
            <textarea
              placeholder=""
              className="w-full p-2 border rounded-lg bg-gray-100"
              disabled
            ></textarea>
          </div>
        </div>
      </div>

      {/* Detailed Report Section */}
      <div className="bg-white p-6 rounded-xl shadow-md">
        <h2 className="text-xl font-semibold mb-4">Detailed Report</h2>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse bg-white">
            <thead>
              <tr className="bg-gray-200 text-left">
                <th className="p-3 border">#</th>
                <th className="p-3 border">Table Name</th>
                <th className="p-3 border">Table Purpose/Definition</th>
                <th className="p-3 border">Column Name</th>
                <th className="p-3 border">Definition</th>
                <th className="p-3 border">Critical Data Element (CDE)</th>
                <th className="p-3 border">Transformation (If Applicable)</th>
                <th className="p-3 border">Sensitivity/Privacy Classification</th>
              </tr>
            </thead>
            <tbody>
              {[1, 2, 3, 4, 5].map((num) => (
                <tr key={num} className="border">
                  <td className="p-3 border">{num}</td>
                  <td className="p-3 border"></td>
                  <td className="p-3 border"></td>
                  <td className="p-3 border"></td>
                  <td className="p-3 border"></td>
                  <td className="p-3 border">Yes/No</td>
                  <td className="p-3 border"></td>
                  <td className="p-3 border"></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default MetadataExtraction;