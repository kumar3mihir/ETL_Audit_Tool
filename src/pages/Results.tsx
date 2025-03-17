
import React from "react";
import { useLocation } from "react-router-dom";
import { Card, CardContent } from "../components/ui/Card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "../components/ui/Table";

interface AuditResult {
  evidence?: string[];
  result?: string[];
}

interface AdditionalQuestion {
  [question: string]: AuditResult;
}

export default function Results() {
  const location = useLocation();
  const auditResults: Record<string, AuditResult | AdditionalQuestion> = location.state?.auditResults || {};

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
    <div className="p-6 w-full"> {/* 👈 Full width */}
      <Card className="mt-6 w-full"> {/* 👈 Full width */}
        <CardContent className="p-6">
          <h3 className="text-lg font-bold mb-4">Audit Results</h3>
          <Table className="w-full"> {/* 👈 Make Table Full Width */}
            <TableHeader>
              <TableRow>
                <TableHead className="w-1/4">Category</TableHead>
                <TableHead className="w-1/4">Result</TableHead>
                <TableHead className="w-2/4">Evidence</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {Object.entries(auditResults).map(([key, value]) => {
                // Handle Additional Questions separately
                if (key === "Additional Questions" && typeof value === "object") {
                  return Object.entries(value).map(([question, details]) => (
                    <TableRow key={question}>
                      <TableCell className="font-bold">{question}</TableCell>
                      <TableCell>{details.result?.join(", ") || "N/A"}</TableCell>
                      <TableCell>{details.evidence?.join("; ") || "N/A"}</TableCell>
                    </TableRow>
                  ));
                }

                // Standard audit categories
                return (
                  <TableRow key={key}>
                    <TableCell className="font-bold">{key}</TableCell>
                    <TableCell>{(value as AuditResult).result?.join(", ") || "N/A"}</TableCell>
                    <TableCell>{(value as AuditResult).evidence?.join("; ") || "N/A"}</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}

