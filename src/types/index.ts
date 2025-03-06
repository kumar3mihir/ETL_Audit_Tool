export interface FileUpload {
  id: string;
  name: string;
  size: number;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
}

export interface DatabaseConnection {
  id: string;
  name: string;
  type: 'mongodb' | 'mysql' | 'sqlserver';
  hostname: string;
  port: number;
  database: string;
  username: string;
  useSsl: boolean;
}

export interface TableMetadata {
  name: string;
  columns: ColumnMetadata[];
  rowCount: number;
  size: string;
}

export interface ColumnMetadata {
  name: string;
  type: string;
  nullable: boolean;
  isPrimary: boolean;
  isForeign: boolean;
  references?: string;
}

export interface Theme {
  isDark: boolean;
  toggleTheme: () => void;
}