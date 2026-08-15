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

import type {
  CommunityFeedback,
} from "@/types/api";

export async function getFeedback(
  options?: {
    limit?: number;
    status?: string;
    sort?: string;
  },
): Promise<CommunityFeedback[]> {
  const params = new URLSearchParams();

  params.set(
    "limit",
    String(options?.limit ?? 20),
  );

  params.set(
    "sort",
    options?.sort ?? "relevance",
  );

  if (options?.status) {
    params.set(
      "status",
      options.status,
    );
  }

  return apiFetch<CommunityFeedback[]>(
    `/api/feedback?${params.toString()}`,
  );
}

export async function getTopFeedback(
  options?: {
    limit?: number;
    status?: string;
  },
): Promise<CommunityFeedback[]> {
  const params = new URLSearchParams();

  params.set(
    "limit",
    String(options?.limit ?? 10),
  );

  params.set(
    "status",
    options?.status ?? "open",
  );

  return apiFetch<CommunityFeedback[]>(
    `/api/feedback/top?${params.toString()}`,
  );
}

export async function getFeedbackById(
  feedbackId: string,
): Promise<CommunityFeedback> {
  return apiFetch<CommunityFeedback>(
    `/api/feedback/${feedbackId}`,
  );
}

export async function getEscalations(params?: {
  status?: string;
  guild_id?: string;
  limit?: number;
  skip?: number;
}) {
  const query = new URLSearchParams();

  if (params?.status)
    query.set("status", params.status);

  if (params?.guild_id)
    query.set("guild_id", params.guild_id);

  if (params?.limit)
    query.set(
      "limit",
      String(params.limit),
    );

  if (params?.skip)
    query.set(
      "skip",
      String(params.skip),
    );

  const response = await fetch(
    `${API_URL}/api/escalations/?${query}`,
    {
      cache: "no-store",
    },
  );

  if (!response.ok) {
    throw new Error(
      "Failed to load escalations.",
    );
  }

  return response.json();
}


export async function updateEscalationStatus(
  id: string,
  status: string,
) {
  const response = await fetch(
    `${API_URL}/api/escalations/${id}/status`,
    {
      method: "PATCH",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        status,
      }),
    },
  );

  if (!response.ok) {
    const data =
      await response.json();

    throw new Error(
      data.detail ||
        "Failed to update escalation.",
    );
  }

  return response.json();
}


export async function sendEscalationMessage(
  id: string,
  message: {
    user_id: string;
    username: string;
    content: string;
  },
) {
  const response = await fetch(
    `${API_URL}/api/escalations/${id}/messages`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(message),
    },
  );

  if (!response.ok) {
    const data =
      await response.json();

    throw new Error(
      data.detail ||
        "Failed to send message.",
    );
  }

  return response.json();
}