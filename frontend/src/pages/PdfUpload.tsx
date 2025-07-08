import React, { useState } from 'react';
import http from '@/lib/http';

const PdfUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await http.post("/api/v1/pdf/upload-pdf", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setMessage(res.data.msg + ": " + res.data.filename);
    } catch (err: any) {
      setMessage(err.response?.data?.detail || "Upload failed");
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Upload PDF</h2>
      <form onSubmit={handleSubmit}>
        <input type="file" accept=".pdf" onChange={handleFileChange} />
        <button type="submit" className="ml-2 px-4 py-2 bg-blue-600 text-white">Upload</button>
      </form>
      {message && <p className="mt-4 text-green-600">{message}</p>}
    </div>
  );
};

export default PdfUpload;
