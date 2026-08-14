import type {
  Document,
  DocumentUploadResponse,
  CommunitySignal,
  AnalyticsOverview,
  AnalyticsActivity,
  AnalyticsTopic,
  KnowledgeAnalytics,
} from "@/types/api";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

// ============================================================
// Generic API Fetch
// ============================================================

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


// ============================================================
// Documents
// ============================================================

export async function getDocuments(): Promise<Document[]> {
  return apiFetch<Document[]>(
    "/api/documents",
  );
}


export async function uploadDocument(
  file: File,
): Promise<DocumentUploadResponse> {
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


// ============================================================
// Analytics Overview
// ============================================================

export async function getAnalyticsOverview(): Promise<AnalyticsOverview> {
  return apiFetch<AnalyticsOverview>(
    "/api/analytics/overview",
  );
}


// ============================================================
// Analytics Activity
// ============================================================

export async function getAnalyticsActivity(
  days: number = 30,
): Promise<AnalyticsActivity[]> {
  return apiFetch<AnalyticsActivity[]>(
    `/api/analytics/activity?days=${days}`,
  );
}


// ============================================================
// Analytics Topics
// ============================================================

export async function getAnalyticsTopics(): Promise<AnalyticsTopic[]> {
  return apiFetch<AnalyticsTopic[]>(
    "/api/analytics/topics",
  );
}


// ============================================================
// Analytics Knowledge
// ============================================================

export async function getAnalyticsKnowledge(
  days: number = 30,
): Promise<KnowledgeAnalytics> {
  return apiFetch<KnowledgeAnalytics>(
    `/api/analytics/knowledge?days=${days}`,
  );
}


// ============================================================
// Community Signals
// ============================================================

export async function getCommunitySignals(): Promise<CommunitySignal[]> {
  return apiFetch<CommunitySignal[]>(
    "/api/community/signals",
  );
}


// ============================================================
// Refresh Community Signals
// ============================================================

export async function refreshCommunitySignals(): Promise<{
  status: string;
  count: number;
  insights: CommunitySignal[];
}> {
  return apiFetch<{
    status: string;
    count: number;
    insights: CommunitySignal[];
  }>(
    "/api/community/signals/refresh",
    {
      method: "POST",
    },
  );
}