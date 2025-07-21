import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getPdfList } from "@/api/pdfApi";
import type {PDFFile } from "@/api/pdfApi";

export const PDFListPage = () => {
  const [pdfs, setPdfs] = useState<PDFFile[]>([]);

  useEffect(() => {
    getPdfList()
      .then(setPdfs)
      .catch(err => console.error("Error loading PDF list", err));
  }, []);

  return (
    <div className="max-w-5xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">📄 Uploaded PDF Files</h1>

      {pdfs.length === 0 ? (
        <p>No PDFs found.</p>
      ) : (
        <table className="w-full border rounded shadow">
          <thead className="bg-gray-100 text-left">
            <tr>
              <th className="p-3">Filename</th>
              <th className="p-3">Uploaded At</th>
              <th className="p-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {pdfs.map((pdf, idx) => (
              <tr key={idx} className="border-t hover:bg-gray-50">
                <td className="p-3">{pdf.filename}</td>
                <td className="p-3">{pdf.upload_time ? new Date(pdf.upload_time).toLocaleString() : "-"}</td>
                <td className="p-3">
                  <Link
                    to={`/pdfs/${pdf.id}`}
                    className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-800"
                  >
                    View Details
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
export default PDFListPage;