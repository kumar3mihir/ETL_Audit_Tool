import axios from 'axios';

// Set base URL to your Flask backend
const API_URL = 'http://localhost:5001/api';  // Update as necessary

// Utility function to handle error responses
const handleError = (error) => {
  console.error('API Error:', error);
  return { error: error.response?.data || error.message };
};

// File Upload API
export const uploadFiles = async (files) => {
  try {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    
    const response = await axios.post(`${API_URL}/files/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

// Process Files API (for schema extraction)
export const processFiles = async (fileIds) => {
  try {
    const response = await axios.post(`${API_URL}/files/process`, { file_ids: fileIds });
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

// Database Connection API
export const connectToDatabase = async (dbType, params) => {
  try {
    const response = await axios.post(`${API_URL}/db/connect`, { type: dbType, params });
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

// Metadata Analysis API (AI)
export const analyzeMetadata = async (schemaData, model = 'gpt-4') => {
  try {
    const response = await axios.post(`${API_URL}/ai/analyze`, { schema: schemaData, model });
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

// Report Generation API
export const generateReport = async (analysisData, reportType = 'pdf') => {
  try {
    const response = await axios.post(`${API_URL}/ai/report`, { analysis: analysisData, type: reportType }, { responseType: 'blob' });
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};
