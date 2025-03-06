import React from "react";

interface ProgressBarProps {
  progress: number;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ progress }) => {
  return (
    <div className="w-full mt-4">
      <h3 className="text-center text-gray-700 mb-2">Processing... {progress}%</h3>
      <div className="relative pt-1">
        <div className="flex mb-2 items-center justify-between">
          <div>
            <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-teal-600 bg-teal-200">
              Processing
            </span>
          </div>
          <div className="text-right">
            <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-teal-600 bg-teal-200">
              {progress}% completed
            </span>
          </div>
        </div>
        <div className="flex mb-2">
          <div className="w-full bg-gray-200 rounded-full">
            <div
              className="bg-teal-500 text-xs leading-none py-1 text-center text-teal-100"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressBar;
