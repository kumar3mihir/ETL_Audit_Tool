import React, { useState } from "react";
import { useNavigate } from "react-router-dom"; // Import for navigation

const MetadataPage: React.FC = () => {
  // Simulate the database connection state
  const [isConnected, setIsConnected] = useState(false); // Initially, not connected

  // Placeholder data for when DB is not connected
  const placeholderData = [
    {
      id: 1,
      name: "",
      purpose: "",
      summary: "",
      createdDate: "",
    },
    {
      id: 2,
      name: "",
      purpose: "",
      summary: "",
      createdDate: "",
    },
    {
      id: 3,
      name: "",
      purpose: "",
      summary: "",
      createdDate: "",
    },
    {
      id: 4,
      name: "",
      purpose: "",
      summary: "",
      createdDate: "",
    },
    {
      id: 5,
      name: "",
      purpose: "",
      summary: "",
      createdDate: "",
    },
  ];

  const navigate = useNavigate(); // Using react-router for navigation

  // Handle navigation after clicking "Extract"
  const handleExtractClick = () => {
    if (isConnected) {
      // Simulate navigation to another page (like metadata analysis)
      navigate("/metadata-analysis"); // Replace with your desired path
    } else {
      alert("Please connect to the database first.");
      navigate("/metadata-analysis");
    }
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="text-3xl font-bold text-gray-900 mb-8 text-center">Database Metadata Extraction</div>

      {/* Overview Section */}
      <div className="bg-white shadow-lg rounded-lg p-6 mb-8">
        <div className="text-xl font-semibold text-gray-700 mb-4">Overview</div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-600">Tables Count:</label>
            <input
              type="text"
              className="w-full border rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder={isConnected ? "Enter number of tables" : "Waiting for database connection..."}
              disabled={!isConnected}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-600">
              Purpose & summary of tables/data stored:
            </label>
            <textarea
              className="w-full border rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder={isConnected ? "Enter summary" : "Waiting for database connection..."}
              disabled={!isConnected}
            />
          </div>
        </div>
      </div>

      {/* Detailed Report Section */}
      <div className="bg-white shadow-lg rounded-lg p-6 mb-8">
        <div className="text-xl font-semibold text-gray-700 mb-4">Detailed Report</div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm text-left border-collapse border border-gray-200">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-3 border border-gray-200">#</th>
                <th className="p-3 border border-gray-200">Table Name</th>
                <th className="p-3 border border-gray-200">Purpose</th>
                <th className="p-3 border border-gray-200">Summary</th>
                <th className="p-3 border border-gray-200">Created Date</th>
                <th className="p-3 border border-gray-200">Download</th>
              </tr>
            </thead>
            <tbody>
              {placeholderData.map((row) => (
                <tr key={row.id} className="hover:bg-gray-50">
                  <td className="p-3 border border-gray-200">{row.id}</td>
                  <td className="p-3 border border-gray-200">{row.name}</td>
                  <td className="p-3 border border-gray-200">
                    <input
                      type="text"
                      defaultValue={row.purpose}
                      className="w-full border rounded-lg p-2 text-sm"
                      disabled={!isConnected}
                    />
                  </td>
                  <td className="p-3 border border-gray-200 text-blue-500 cursor-pointer">{row.summary}</td>
                  <td className="p-3 border border-gray-200">{row.createdDate}</td>
                  <td className="p-3 border border-gray-200 text-center">
                    <button
                      className={`text-blue-500 hover:underline ${!isConnected && "cursor-not-allowed text-gray-300"}`}
                      disabled={!isConnected}
                    >
                      ⬇
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination and Download All Button */}
        <div className="mt-6 flex justify-between items-center">
          <div className="flex space-x-2">
            <button className="px-4 py-2 border rounded-lg text-sm">1</button>
            <button className="px-4 py-2 border rounded-lg text-sm">2</button>
            <button className="px-4 py-2 border rounded-lg text-sm">3</button>
          </div>
          <button
            className={`px-6 py-3 bg-blue-600 text-white rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 ${!isConnected && "cursor-not-allowed bg-gray-300"}`}
            disabled={!isConnected}
            onClick={handleExtractClick}
          >
            Extract
          </button>
        </div>
      </div>

      {/* Button to simulate database connection */}
      <div className="text-center mt-6">
        <button
          className="px-6 py-3 bg-green-600 text-white rounded-lg shadow-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
          onClick={() => setIsConnected(true)}
        >
          Connect to Database
        </button>
      </div>
    </div>
  );
};

export default MetadataPage;




// // /src/pages/metadata_extraction.tsx
// import React from "react";

// const MetadataPage: React.FC = () => {
//   // Example data for the table
//   const tableData = [
//     {
//       id: 1,
//       name: "Customer table",
//       purpose: "text",
//       summary: "Click to see",
//       createdDate: "25/11/2023",
//     },
//     {
//       id: 2,
//       name: "Products table",
//       purpose: "text",
//       summary: "Click to see",
//       createdDate: "27/08/2023",
//     },
//     {
//       id: 3,
//       name: "Nisi nostrud amet mol",
//       purpose: "",
//       summary: "Click to see",
//       createdDate: "07/02/2023",
//     },
//     {
//       id: 4,
//       name: "In labore commodo ip",
//       purpose: "text",
//       summary: "Click to see",
//       createdDate: "30/06/2023",
//     },
//     {
//       id: 5,
//       name: "Cillum adipisicing non",
//       purpose: "",
//       summary: "Click to see",
//       createdDate: "14/05/2023",
//     },
//     // Add more rows as needed
//   ];

//   return (
//     <div className="p-6 bg-gray-50 min-h-screen">
//       {/* Header */}
//       <div className="text-2xl font-bold mb-6">Database Name</div>

//       {/* Overview Section */}
//       <div className="bg-white shadow rounded-lg p-6 mb-6">
//         <div className="text-xl font-semibold mb-4">Overview</div>
//         <div className="grid grid-cols-2 gap-4">
//           <div>
//             <label className="block text-sm font-medium mb-1">Tables Count:</label>
//             <input
//               type="text"
//               className="w-full border rounded p-2 text-sm"
//               placeholder="Number of tables"
//             />
//           </div>
//           <div>
//             <label className="block text-sm font-medium mb-1">
//               Purpose & summary of what kind of table or data are stored:
//             </label>
//             <textarea
//               className="w-full border rounded p-2 text-sm"
//               placeholder="Enter details"
//             />
//           </div>
//         </div>
//       </div>

//       {/* Detailed Report Section */}
//       <div className="bg-white shadow rounded-lg p-6">
//         <div className="text-xl font-semibold mb-4">Detailed Report</div>
//         <div className="overflow-x-auto">
//           <table className="min-w-full text-sm text-left border-collapse border border-gray-200">
//             <thead>
//               <tr className="bg-gray-100 border-b">
//                 <th className="p-2 border border-gray-200">#</th>
//                 <th className="p-2 border border-gray-200">Table Name</th>
//                 <th className="p-2 border border-gray-200">Purpose</th>
//                 <th className="p-2 border border-gray-200">Summary</th>
//                 <th className="p-2 border border-gray-200">Created Date</th>
//                 <th className="p-2 border border-gray-200">Download</th>
//               </tr>
//             </thead>
//             <tbody>
//               {tableData.map((row) => (
//                 <tr key={row.id} className="hover:bg-gray-50">
//                   <td className="p-2 border border-gray-200">{row.id}</td>
//                   <td className="p-2 border border-gray-200">{row.name}</td>
//                   <td className="p-2 border border-gray-200">
//                     <input
//                       type="text"
//                       defaultValue={row.purpose}
//                       className="w-full border rounded p-1"
//                     />
//                   </td>
//                   <td className="p-2 border border-gray-200 text-blue-500 cursor-pointer">
//                     {row.summary}
//                   </td>
//                   <td className="p-2 border border-gray-200">{row.createdDate}</td>
//                   <td className="p-2 border border-gray-200 text-center">
//                     <button className="text-blue-500 hover:underline">⬇</button>
//                   </td>
//                 </tr>
//               ))}
//             </tbody>
//           </table>
//         </div>
//         {/* Pagination and Download All Button */}
//         <div className="mt-4 flex justify-between items-center">
//           <div className="flex space-x-2">
//             <button className="px-3 py-1 border rounded text-sm">1</button>
//             <button className="px-3 py-1 border rounded text-sm">2</button>
//             <button className="px-3 py-1 border rounded text-sm">3</button>
//           </div>
//           <button className="px-4 py-2 bg-blue-500 text-white rounded shadow hover:bg-blue-600">
//             Download All Files
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default MetadataPage;


