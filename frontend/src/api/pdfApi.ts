
import http from "../lib/http";

export interface PDFFile {
  id: string;
  filename: string;
  upload_time?: string;
}

export interface PDFDetail {
  id: string;
  filename: string;
  doc_type: string;
  extracted_data: string | Record<string, any> | any[];
  status: string;
}

export interface PromptPayload {
  text: string;
  goal?: string;
  doc_type?: string;
}

export interface PromptResponse {
  response: string;
}

export interface ChunkList {
  filename: string;
  chunk_count?: string;
}
export interface ChunkSummary {
  id: string;
  chunk_num: number;
  page: number | null;
  content: string;
  char_count: number;
  processed: boolean;
  has_analysis: boolean;
}

export async function ragQuery(question: string, docType: string = "default") {
  const res = await http.post<{ result: string }>("/rag/query", {
    question,
    doc_type: docType,
  });
  return res.result;
}

export const uploadPDF = async (formData: FormData) => {
  const res = await http.post("/pdfs/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res;  // Make sure you return res.data here
};

export const getPdfList = async (): Promise<PDFFile[]> => {
  const response = await http.get<PDFFile[]>("/pdfs/");
  return response; // <-- .data contains the actual payload
};

export const getChunks = async (): Promise<ChunkList[]> => {
  const response = await http.get<ChunkList[]>("/chunks/");
  return response; // <-- .data contains the actual payload
};

export async function getPDFChunks(pdfId: string): Promise<ChunkSummary[]> {
  const response = await http.get<ChunkSummary[]>(`/pdfs/${pdfId}/chunks`);
  return response;
};

export async function getPDFDetail(id: string): Promise<PDFDetail> {
  const res = await http.get<PDFDetail>(`/pdfs/${id}`);

  const parsed = typeof res.extracted_data === "string"
    ? JSON.parse(res.extracted_data)
    : res.extracted_data;

  return {
    id: res.id,
    filename: res.filename,
    doc_type: res.doc_type,
    extracted_data: parsed,
    status: res.status,
  };
}


export async function generateAIResponse(data: PromptPayload): Promise<PromptResponse> {
  try {
    const res = await http.post<PromptResponse>("/prompt/engineer", data);
    return res;
  } catch (error: any) {
    // Graceful error handling
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    throw new Error("Failed to generate AI response");
  }
}