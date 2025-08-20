import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getPDFChunks } from "../api/pdfApi";
import type { ChunkSummary } from "../api/pdfApi";

export default function ChunkDetailsPage() {
  const { id } = useParams<{ id: string }>(); // PDF ID from route
  const [chunks, setChunks] = useState<ChunkSummary[]>([]);
  const [selectedChunk, setSelectedChunk] = useState<ChunkSummary | null>(null);

  useEffect(() => {
    if (id) {
      getPDFChunks(id).then(setChunks);
    }
  }, [id]);

  return (
    <div className="flex h-screen">
      {/* Sidebar / TOC */}
      <aside className="w-64 bg-gray-100 p-4 border-r overflow-y-auto">
        <h2 className="text-lg font-bold mb-3">Chunks</h2>
        <ul className="space-y-2">
          {chunks.map((chunk) => (
            <li
              key={chunk.id}
              className={`p-2 rounded cursor-pointer hover:bg-gray-200 ${
                selectedChunk?.id === chunk.id ? "bg-blue-100" : ""
              }`}
              onClick={() => setSelectedChunk(chunk)}
            >
              <span className="font-semibold">Chunk {chunk.chunk_num}</span>
              <p className="text-xs text-gray-600 truncate">
                {chunk.content}
              </p>
            </li>
          ))}
        </ul>
      </aside>

      {/* Main Chunk Content */}
      <main className="flex-1 p-6 overflow-y-auto">
        {selectedChunk ? (
          <div>
            <h2 className="text-xl font-bold mb-4">
              Chunk {selectedChunk.chunk_num} (Page {selectedChunk.page ?? "?"})
            </h2>
            <p className="mb-2 text-gray-700">
              Characters: {selectedChunk.char_count} |{" "}
              {selectedChunk.processed ? "Processed" : "⏳ Not processed"}
            </p>
            <div className="whitespace-pre-wrap border p-4 rounded bg-gray-50">
              {selectedChunk.content}
            </div>
          </div>
        ) : (
          <p className="text-gray-500">Select a chunk from the sidebar</p>
        )}
      </main>
    </div>
  );
}
