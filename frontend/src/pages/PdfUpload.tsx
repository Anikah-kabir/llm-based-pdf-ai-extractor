import React, { useState } from 'react';
import { useNavigate } from "react-router-dom";
import { uploadPDF } from '@/api/pdfApi';

import loaderImage from '@/assets/loader.gif'; // your loader image

const PdfUpload: React.FC = () => {
  const navigate = useNavigate();

  const [file, setFile] = useState<File | null>(null);
  const [docType, setDocType] = useState("default");
  const [goal, setGoal] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setMessage("Please select a PDF file");
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("doc_type", docType);
      formData.append("goal", goal);
      
      const res = await uploadPDF(formData);
      setMessage(`Upload successful: ${res.filename}`);
      navigate("/pdfs");
    } catch (err: any) {
      setMessage(err.response?.data?.detail || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded shadow max-w-lg mx-auto">
      <h2 className="text-xl font-bold mb-4">Upload PDF</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          className="block w-full border rounded px-3 py-2"
        />

        <select
          value={docType}
          onChange={(e) => setDocType(e.target.value)}
          className="block w-full border rounded px-3 py-2"
        >
          <option value="default">General</option>
          <option value="medical">Medical</option>
          <option value="invoice">Invoice</option>
          <option value="resume">Resume</option>
        </select>

        <input
          type="text"
          placeholder="Enter goal (optional)"
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          className="block w-full border rounded px-3 py-2"
        />

        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          disabled={loading}
        >
          {loading ? "Uploading..." : "Upload"}
        </button>
      </form>

      {loading && (
        <div className="flex justify-center mt-4">
          <img src={loaderImage} alt="Uploading..." className="w-12 h-12" />
        </div>
      )}

      {message && (
        <p className="mt-4 text-green-700 font-medium">{message}</p>
      )}
    </div>
  );
};

export default PdfUpload;
