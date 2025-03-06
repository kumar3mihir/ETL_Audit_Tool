// /src/components/DatabaseConnection.tsx
import React, { useState } from 'react';
import { Database, Server, Lock } from 'lucide-react';
import type { DatabaseConnection } from '../types';

export const DatabaseConnectionForm = () => {
  const [connection, setConnection] = useState<Partial<DatabaseConnection>>({
    type: 'mysql',
    useSsl: false,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle connection logic here
  };

  const handleExtract = () => {
    // Logic to handle metadata extraction after connection is established
    alert('Extracting metadata...');
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <form onSubmit={handleSubmit} className="space-y-6 bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <div className="space-y-4">
          {/* Database Type */}
          <label className="block">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-200">Database Type</span>
            <select
              value={connection.type}
              onChange={(e) => setConnection((prev) => ({ ...prev, type: e.target.value as DatabaseConnection['type'] }))}
              className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700"
            >
              <option value="mysql">MySQL</option>
              <option value="mongodb">MongoDB</option>
              <option value="sqlserver">SQL Server</option>
            </select>
          </label>

          {/* Hostname */}
          <label className="block">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-200">Hostname</span>
            <div className="mt-1 relative rounded-md shadow-sm">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Server className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                value={connection.hostname || ''}
                onChange={(e) => setConnection((prev) => ({ ...prev, hostname: e.target.value }))}
                className="block w-full pl-10 rounded-md border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700"
                placeholder="localhost"
              />
            </div>
          </label>

          <div className="grid grid-cols-2 gap-4">
            {/* Port */}
            <label className="block">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-200">Port</span>
              <input
                type="number"
                value={connection.port || ''}
                onChange={(e) => setConnection((prev) => ({ ...prev, port: parseInt(e.target.value) }))}
                className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700"
              />
            </label>

            {/* Database Name */}
            <label className="block">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-200">Database Name</span>
              <input
                type="text"
                value={connection.database || ''}
                onChange={(e) => setConnection((prev) => ({ ...prev, database: e.target.value }))}
                className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700"
              />
            </label>
          </div>

          {/* Username */}
          <label className="block">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-200">Username</span>
            <input
              type="text"
              value={connection.username || ''}
              onChange={(e) => setConnection((prev) => ({ ...prev, username: e.target.value }))}
              className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700"
            />
          </label>

          {/* Password */}
          <label className="block">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-200">Password</span>
            <div className="mt-1 relative rounded-md shadow-sm">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="password"
                className="block w-full pl-10 rounded-md border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700"
              />
            </div>
          </label>

          {/* SSL Checkbox */}
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={connection.useSsl}
              onChange={(e) => setConnection((prev) => ({ ...prev, useSsl: e.target.checked }))}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700 dark:text-gray-200">Use SSL/TLS connection</span>
          </label>
        </div>

        {/* Buttons */}
        <div className="flex space-x-4">
          {/* Connect Button */}
          <button
            type="submit"
            className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Connect
          </button>

          {/* Test Connection Button */}
          <button
            type="button"
            className="flex-1 bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-200 px-4 py-2 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
          >
            Test Connection
          </button>

          {/* Extract Button */}
          <button
            type="button"
            onClick={handleExtract}
            className="flex-1 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-500 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
          >
            Extract
          </button>
        </div>
      </form>
    </div>
  );
};
