import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { Hero } from './components/Hero';
import ConnectionPage from './pages/ConnectionPage';
import MetadataPage from "./pages/metadata_extraction";
import EtlAudit from "./pages/EtlAudit";
import Result from './pages/Results';
import MetadataExtraction from './pages/meta_excel';

function App() {
  return (
    <ThemeProvider>
      <Router>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
          <Routes>
            {/* Home Page */}
            <Route path="/" element={<Hero />} />
            {/* ETL Audit Page */}
            <Route path="/etl" element={<EtlAudit />} />
            {/* Database Connection Page */}
            <Route path="/connection" element={<ConnectionPage />} />
            {/* Results Page (Fetches audit results from navigation state) */}
            <Route path="/results" element={<Result />} />
            {/* Metadata Extraction Page */}
            <Route path="/metadata" element={<MetadataPage />} />
            {/* Excel Sheet Viewer */}
            <Route path="/excel" element={<MetadataExtraction />} />
          </Routes>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
