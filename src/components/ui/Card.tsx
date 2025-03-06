import { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string; // Add className prop
}

export function Card({ children, className = "" }: CardProps) {
  return <div className={`bg-white shadow-md rounded-lg overflow-hidden ${className}`}>{children}</div>;
}

interface CardContentProps {
  children: ReactNode;
  className?: string;
}

export function CardContent({ children, className = "" }: CardContentProps) {
  return <div className={`p-4 ${className}`}>{children}</div>;
}