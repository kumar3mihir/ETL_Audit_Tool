// /src/components/ResultPage/LeftSide/AuditResultsWithMetadata.tsx   //this is /results
import React from "react";
import { useLocation } from "react-router-dom";
import { Card, CardContent } from "../../ui/Card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "../../ui/Table";

interface AuditMetadata {
  timestamp?: string;
  folderName?: string;
  fileName?: string;
}

interface AuditResult {
  evidence?: string[];
  result?: string[];
}



const AuditResultsWithMetadata: React.FC = () => {
  const location = useLocation();
  const auditResults: Record<string, AuditResult> = location.state?.auditResults || {};
  const auditMetadata: AuditMetadata = location.state?.auditMetadata || {};

  if (!auditResults || Object.keys(auditResults).length === 0) {
    return (
      <div className="p-6 text-center">
        <h3 className="text-lg font-bold">No Audit Results Found</h3>
        <p>Please upload a file and run the audit.</p>
      </div>
    );
  }

  return (
    <div className="flex w-full max-w-screen-xl mx-auto gap-6 mt-8 px-6">
      {/* Left Side - Audit Metadata & Results */}
      <div className="w-2/3 bg-white p-6 rounded-lg shadow-md">
        {/* File Metadata */}
        <Card className="mb-4">
          <CardContent className="p-4">
            <h3 className="text-lg font-bold mb-2">Audit Metadata</h3>
            <p><strong>Audit Timestamp:</strong> {auditMetadata.timestamp || "N/A"}</p>
            <p><strong>Audit Folder:</strong> {auditMetadata.folderName || "N/A"}</p>
            <p><strong>File Name:</strong> {auditMetadata.fileName || "N/A"}</p>
          </CardContent>
        </Card>

        {/* Audit Results */}
        <Card className="mt-4">
          <CardContent className="p-4">
            <h3 className="text-lg font-bold mb-4">Audit Results</h3>
            <Table className="w-full">
              <TableHeader>
                <TableRow>
                  <TableHead className="w-1/4">Category</TableHead>
                  <TableHead className="w-1/4">Result</TableHead>
                  <TableHead className="w-1/2">Evidence</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {Object.entries(auditResults).map(([key, value]) => (
                  <TableRow key={key}>
                    <TableCell className="font-bold">{key}</TableCell>
                    <TableCell>{value.result?.join(", ") || "N/A"}</TableCell>
                    <TableCell>{value.evidence?.join("; ") || "N/A"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>

      {/* Right Side - Chat Box */}
     
    </div>
  );
};

export default AuditResultsWithMetadata;