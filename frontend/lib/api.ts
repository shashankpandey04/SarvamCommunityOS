import type {
  Document,
  DocumentUploadResponse,
} from "@/types/api";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

export async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(
    `${API_URL}${endpoint}`,
    {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
      cache: "no-store",
    },
  );

  if (!response.ok) {
    const error = await response.text();

    throw new Error(
      error || `API request failed: ${response.status}`,
    );
  }

  return response.json();
}

export async function getDocuments() {
  return apiFetch<Document[]>(
    "/api/documents"
  );
}

export async function uploadDocument(
  file: File,
) {

  const formData = new FormData();

  formData.append(
    "file",
    file,
  );

  return apiFetch<DocumentUploadResponse>(
    "/api/documents/upload",
    {
      method: "POST",
      body: formData,
    },
  );
}