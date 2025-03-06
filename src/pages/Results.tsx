import React from "react";
import { useLocation } from "react-router-dom";
import { Card, CardContent } from "../components/ui/Card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "../components/ui/Table";

interface AuditResult {
  evidence?: string[];  // Optional to prevent undefined errors
  result?: string[];
}

export default function Results() {
  const location = useLocation();
  const auditResults: Record<string, AuditResult> = location.state?.auditResults || {};

  console.log("📌 Location State:", location.state);
  console.log("📌 Audit Results:", auditResults);

  if (!auditResults || Object.keys(auditResults).length === 0) {
    console.log("🚨 No audit results found, showing fallback message.");
    return (
      <div className="p-6 text-center">
        <h3 className="text-lg font-bold">No Audit Results Found</h3>
        <p>Please upload a file and run the audit.</p>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <Card className="mt-6">
        <CardContent className="p-6">
          <h3 className="text-lg font-bold mb-4">Audit Results</h3>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Category</TableHead>
                <TableHead>Result</TableHead>
                <TableHead>Evidence</TableHead>
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
  );
}
