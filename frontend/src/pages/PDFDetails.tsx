import { useEffect, useState, type ReactNode } from "react";
import { useParams } from "react-router-dom";
import { getPDFDetail } from "../api/pdfApi";
import type { PDFDetail } from "../api/pdfApi";


// Recursive function to render nested JSON
const renderData = (data: any): ReactNode => {
  if (typeof data === "string" || typeof data === "number") {
    return <span>{data}</span>;
  }

  if (Array.isArray(data)) {
    return (
      <ul style={{ paddingLeft: "1rem" }}>
        {data.map((item, index) => (
          <li key={index}>{renderData(item)}</li>
        ))}
      </ul>
    );
  }

  if (typeof data === "object" && data !== null) {
    return (
      <div style={{ paddingLeft: "1rem", borderLeft: "2px solid #ddd", marginBottom: "1rem" }}>
        {Object.entries(data).map(([key, value]) => (
          <div key={key} style={{ marginBottom: "0.5rem" }}>
            <strong>{key}:</strong> {renderData(value)}
          </div>
        ))}
      </div>
    );
  }

  return <span>{String(data)}</span>;
};

const PDFDetails = () => {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<PDFDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    console.log('tttt');
console.log(id);
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
      <h2 className="text-xl font-bold mb-4">PDF Details: {data.filename}</h2>
      <div className="bg-white shadow rounded p-4">
        {renderData(data.extracted_data)}
      </div>
    </div>
  );
};

export default PDFDetails;
