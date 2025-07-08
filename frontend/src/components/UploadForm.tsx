import { useState } from "react";
import http from "../lib/http";

export default function UploadForm() {
  const [file, setFile] = useState<File | null>(null);

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    if (!file) return alert("Choose a file");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await http.post("/pdf/upload", formData);
      console.log(res);
      alert("Uploaded successfully");
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4">
      <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
      <button type="submit" className="btn">Upload</button>
    </form>
  );
}
