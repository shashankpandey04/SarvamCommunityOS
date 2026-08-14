// ============================================================
// Community Overview
// ============================================================

export interface CommunityOverview {
  members: number;
  messages: number;
  questions: number;
  resolved: number;
  escalated: number;
  resolution_rate: number;
}


// ============================================================
// Community Trends
// ============================================================

export interface CommunityTrend {
  topic: string;
  mentions: number;
}


// ============================================================
// Community Insights / Signals
// ============================================================

export interface InsightMetric {
  current_questions?: number;
  previous_questions?: number;
  growth_percent?: number;

  occurrences?: number;
  question?: string;
}

export interface InsightAction {
  type: string;
  target: string;
}

export interface CommunityInsight {
  type: string;

  severity:
    | "low"
    | "medium"
    | "high";

  title: string;

  message: string;

  suggestion: string;

  topic?: string;

  metric: InsightMetric;

  action: InsightAction;

  created_at: string;

  updated_at: string;
}


// ============================================================
// Generic API Response
// ============================================================

export interface APIError {
  detail: string;
}


// ============================================================
// Health
// ============================================================

export interface HealthResponse {
  status: string;
  service: string;
}

// ============================================================
// Analytics
// ============================================================

export interface AnalyticsOverview {
  total_questions: number;
  resolved: number;
  escalated: number;
  knowledge_found: number;
  sarvam_fallback: number;
  resolution_rate: number;
  knowledge_coverage_rate: number;
  fallback_rate: number;
}

export interface AnalyticsActivity {
  date: string;
  messages: number;
  questions: number;
  resolved: number;
  escalated: number;
  fallback: number;
}

export interface AnalyticsTopic {
  topic: string;
  questions: number;
  resolved: number;
  escalated: number;
  knowledge_found: number;
  sarvam_fallback: number;
  resolution_rate: number;
}

export interface AnalyticsPeriod {
  days: number | null;
  start: string | null;
  end: string;
}

export interface AnalyticsKnowledge {
  period: AnalyticsPeriod;

  knowledge: {
    total: number;
    official: number;
    generated: number;
  };

  candidates: {
    total: number;
    pending: number;
    approved: number;
    rejected: number;
  };
}

export interface TrendingTopic {
  topic: string;
  mentions: number;
}

export interface CommunitySignal {
  type: string;
  severity: "low" | "medium" | "high" | "critical";
  title: string;
  message: string;
  suggestion?: string;

  topic?: string;

  metric?: {
    current_questions?: number;
    previous_questions?: number;
    growth_percent?: number;

    occurrences?: number;
    question?: string;

    [key: string]: unknown;
  };

  action?: {
    type: string;
    target: string;
  };

  created_at: string;
  updated_at: string;
}

export interface Document {
  _id: string;
  filename: string;
  status: "processing" | "completed" | "failed";
  source: string;
  knowledge_count?: number;
  error?: string;
  created_at: string;
  updated_at: string;
}

export interface DocumentUploadResponse {
  status: "completed";
  document_id: string;
  filename: string;
  sections: number;
  knowledge_ids: string[];
}