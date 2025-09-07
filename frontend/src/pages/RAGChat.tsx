import React, { useState } from "react";
import { ragQuery } from '@/api/pdfApi';

interface Message {
  sender: "user" | "ai";
  text: string;
}

const RAGChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [docType, setDocType] = useState("default");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const aiResponse = await ragQuery(input, docType);
      const answerText =
      aiResponse?.result?.answer || "⚠️ No response received from AI.";
      
      const aiMessage: Message = { sender: "ai", text: answerText };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      const errorMessage: Message = { sender: "ai", text: "❌ No relevant information found in the knowledge base.e" };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      setInput("");
    }
  };

  return (
    <div style={{ maxWidth: "800px", margin: "auto", padding: "20px" }}>
      <h2>📄 RAG Chat Assistant</h2>

      {/* Document Type Dropdown */}
      <select
        value={docType}
        onChange={(e) => setDocType(e.target.value)}
        style={{ marginBottom: "10px", padding: "6px" }}
      >
        <option value="default">General</option>
        <option value="medical">Medical</option>
        <option value="invoice">Invoice</option>
        <option value="resume">Resume</option>
      </select>

      {/* Chat Window */}
      <div
        style={{
          border: "1px solid #ccc",
          padding: "10px",
          borderRadius: "5px",
          height: "400px",
          overflowY: "auto",
          marginBottom: "10px",
          backgroundColor: "#f9f9f9",
        }}
      >
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              textAlign: msg.sender === "user" ? "right" : "left",
              margin: "5px 0",
            }}
          >
            <span
              style={{
                display: "inline-block",
                padding: "10px",
                borderRadius: "8px",
                backgroundColor: msg.sender === "user" ? "#007bff" : "#e5e5ea",
                color: msg.sender === "user" ? "white" : "black",
                maxWidth: "70%",
              }}
            >
              {msg.text}
            </span>
          </div>
        ))}
        {loading && <p>⏳ Thinking...</p>}
      </div>

      {/* Input Box */}
      <div style={{ display: "flex", gap: "10px" }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask something..."
          style={{ flex: 1, padding: "10px" }}
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          style={{ padding: "10px 20px", backgroundColor: "#007bff", color: "white", border: "none" }}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default RAGChat;
