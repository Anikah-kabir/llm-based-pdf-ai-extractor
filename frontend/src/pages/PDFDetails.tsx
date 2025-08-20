import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getPDFDetail } from "../api/pdfApi";
import type { PDFDetail } from "../api/pdfApi";

// ✅ Improved rendering
const renderData = (raw: any) => {
  if (!raw) return <p>No data</p>;

  // Case: Array of documents (multiple objects)
  if (Array.isArray(raw)) {
    return (
      <div className="space-y-4">
        {raw.map((doc, idx) => (
          <div
            key={idx}
            className="border rounded p-3 bg-gray-50 shadow-sm"
          >
            <h3 className="font-semibold text-lg mb-2">
              Document {idx + 1}
            </h3>
            <ul className="list-disc pl-5 space-y-1">
              {Object.entries(doc).map(([k, v]) => (
                <li key={k}>
                  <strong>{k}:</strong>{" "}
                  {typeof v === "object" ? JSON.stringify(v) : String(v)}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    );
  }

  // Case: Single JSON object
  if (typeof raw === "object") {
    return (
      <div className="border rounded p-3 bg-gray-50 shadow-sm">
        <ul className="list-disc pl-5 space-y-1">
          {Object.entries(raw).map(([k, v]) => (
            <li key={k}>
              <strong>{k}:</strong>{" "}
              {typeof v === "object" ? JSON.stringify(v) : String(v)}
            </li>
          ))}
        </ul>
      </div>
    );
  }

  // Case: Plain string
  return <p>{raw}</p>;
};

const PDFDetails = () => {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<PDFDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    getPDFDetail(id)
      .then(setData)
      .catch(err => {
        console.error("Error loading PDF detail", err);
        setError("Failed to load PDF details.");
      });
  }, [id]);

  if (error) return <div>{error}</div>;
  if (!data) return <div>Loading...</div>;

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <h2 className="text-xl font-bold mb-4">
        PDF Details: {data.filename} | Doc Type: {data.doc_type}
      </h2>
      <div className="bg-white shadow rounded p-4">
        {renderData(data.extracted_data)}
      </div>
    </div>
  );
};

export default PDFDetails;
