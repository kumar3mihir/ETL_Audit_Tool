import React from "react";

interface TableProps extends React.HTMLAttributes<HTMLTableElement> {
  children: React.ReactNode;
}

export function Table({ children, className, ...props }: TableProps) {
  return (
    <div className="overflow-x-auto">
      <table className={`min-w-full border-collapse border border-gray-300 ${className}`} {...props}>
        {children}
      </table>
    </div>
  );
}

interface TableSectionProps extends React.HTMLAttributes<HTMLTableSectionElement> {
  children: React.ReactNode;
}

export function TableHeader({ children, className, ...props }: TableSectionProps) {
  return <thead className={`bg-gray-100 ${className}`} {...props}>{children}</thead>;
}

export function TableBody({ children, className, ...props }: TableSectionProps) {
  return <tbody className={className} {...props}>{children}</tbody>;
}

interface TableRowProps extends React.HTMLAttributes<HTMLTableRowElement> {
  children: React.ReactNode;
}

export function TableRow({ children, className, ...props }: TableRowProps) {
  return <tr className={`border-b border-gray-300 ${className}`} {...props}>{children}</tr>;
}

interface TableCellProps extends React.HTMLAttributes<HTMLTableCellElement> {
  children: React.ReactNode;
}

export function TableHead({ children, className, ...props }: TableCellProps) {
  return <th className={`px-4 py-2 text-left font-semibold ${className}`} {...props}>{children}</th>;
}

export function TableCell({ children, className, ...props }: TableCellProps) {
  return <td className={`px-4 py-2 ${className}`} {...props}>{children}</td>;
}