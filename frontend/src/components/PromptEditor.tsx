import { useState } from "react";
import { generateAIResponse } from "@/api/pdfApi"; // Ensure this path is correct based on your project structure

export default function PromptEditor() {
  const [text, setText] = useState("");
  const [goal, setGoal] = useState("");
  const [docType, setDocType] = useState("default");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    setLoading(true);
    setError("");
    setResponse("");

    try {
      const res = await generateAIResponse({
        text,
        goal,
        doc_type: docType,
      });

      console.log("AI raw response:", res);

      // Check if backend returned `response` field
      if (res?.response) {
        setResponse(res.response);
      } else {
        setResponse("No response received.");
      }
    } catch (err: any) {
      setError(err?.message || "An error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "800px", margin: "auto", padding: "20px" }}>
      <h2>Prompt Engineering Playground</h2>

      <label>
        <strong>Extracted Text</strong>
      </label>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={8}
        style={{ width: "100%", marginBottom: "10px" }}
        placeholder="Paste extracted PDF text here"
      />

      <label>
        <strong>Optional Goal</strong>
      </label>
      <input
        value={goal}
        onChange={(e) => setGoal(e.target.value)}
        placeholder="e.g., Extract patient instructions or tabular data"
        style={{ width: "100%", marginBottom: "10px", padding: "8px" }}
      />

      <label>
        <strong>Document Type</strong>
      </label>
      <select
        value={docType}
        onChange={(e) => setDocType(e.target.value)}
        style={{ width: "100%", marginBottom: "20px", padding: "8px" }}
      >
        <option value="default">General</option>
        <option value="medical">Medical</option>
        <option value="invoice">Invoice</option>
        <option value="resume">Resume</option>
      </select>

      <button
        onClick={handleSubmit}
        disabled={loading || !text}
        style={{
          padding: "10px 20px",
          backgroundColor: "#007bff",
          color: "white",
          border: "none",
          cursor: "pointer",
        }}
      >
        {loading ? "Generating..." : "Generate AI Response"}
      </button>

      {error && (
        <p style={{ color: "red", marginTop: "10px" }}>
          {error}
        </p>
      )}

      <h3 style={{ marginTop: "30px" }}>🧾 AI Response:</h3>
      <pre
        style={{
          backgroundColor: "#f4f4f4",
          padding: "15px",
          borderRadius: "5px",
          whiteSpace: "pre-wrap",
          maxHeight: "400px",
          overflow: "auto",
        }}
      >
        {response}
      </pre>
    </div>
  );
}
