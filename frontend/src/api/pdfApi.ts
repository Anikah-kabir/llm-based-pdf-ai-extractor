
import http from "../lib/http";

export interface PDFFile {
  id: string;
  filename: string;
  upload_time?: string;
}

export interface PDFDetail {
  id: string;
  filename: string;
  extracted_data: Record<string, any>; 
}

export interface PromptPayload {
  text: string;
  goal?: string;
  doc_type?: string;
}

export interface PromptResponse {
  response: string;
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

export async function getPDFDetail(id: string): Promise<PDFDetail> {
  const res = await http.get<PDFDetail>(`/pdfs/${id}`);

  const parsed = typeof res.extracted_data === "string"
    ? JSON.parse(res.extracted_data)
    : res.extracted_data;

  return {
    id: res.id,
    filename: res.filename,
    extracted_data: parsed,
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