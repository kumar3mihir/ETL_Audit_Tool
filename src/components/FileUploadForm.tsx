import React from "react";

interface FileUploadFormProps {
  onFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSubmit: (e: React.FormEvent) => void;
  file: File | null;
  additionalQuestions: string;
  onInputChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
}

const FileUploadForm: React.FC<FileUploadFormProps> = ({
  onFileChange,
  onSubmit,
  file,
  additionalQuestions,
  onInputChange,
}) => {
    return (
    <div className="max-w-xl mx-auto p-6 bg-white shadow-lg rounded-lg">
      <h2 className="text-3xl font-semibold text-center text-gray-700 mb-4">
        Upload Your ETL Script
      </h2>
      <form onSubmit={onSubmit} className="space-y-4">
        <div className="flex flex-col">
          <label htmlFor="file" className="text-gray-600">
            Choose ETL Script File
          </label>
          <input
            type="file"
            id="file"
            onChange={onFileChange}
            className="mt-2 p-2 border border-gray-300 rounded"
          />
          {file && (
            <p className="mt-2 text-gray-600">
              Selected file: {file.name}
            </p>
          )}
        </div>
        <div className="flex flex-col">
          <label htmlFor="additionalQuestions" className="text-gray-600">
            Additional Questions
          </label>
          <textarea
            id="additionalQuestions"
            value={additionalQuestions}
            onChange={onInputChange}
            className="mt-2 p-2 border border-gray-300 rounded"
          />
        </div>
        <button
          type="submit"
          className="w-full py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Submit
        </button>
      </form>
    </div>
  );
};

export default FileUploadForm;