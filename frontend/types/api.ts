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

  [key: string]: unknown;
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
    | "high"
    | "critical";

  title: string;

  message: string;

  suggestion?: string;

  topic?: string;

  metric?: InsightMetric;

  action?: InsightAction;

  created_at: string;

  updated_at: string;
}


// ============================================================
// Community Signal
// ============================================================

export interface CommunitySignal {
  type: string;

  severity:
    | "low"
    | "medium"
    | "high"
    | "critical";

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


// ============================================================
// Analytics Period
// ============================================================

export interface AnalyticsPeriod {
  days: number | null;
  start: string | null;
  end: string;
}


// ============================================================
// Knowledge Analytics
// ============================================================

export interface KnowledgeAnalytics {
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


// ============================================================
// Trending Topic
// ============================================================

export interface TrendingTopic {
  topic: string;
  mentions: number;
}


// ============================================================
// Documents
// ============================================================

export interface Document {
  _id: string;

  filename: string;

  status:
    | "processing"
    | "completed"
    | "failed";

  source: string;

  knowledge_count?: number;

  error?: string;

  created_at: string;

  updated_at: string;
}


// ============================================================
// Document Upload
// ============================================================

export interface DocumentUploadResponse {
  status: "completed";

  document_id: string;

  filename: string;

  sections: number;

  knowledge_ids: string[];
}

export interface AnalyticsKnowledge {
  period: {
    days: number | null;
    start: string | null;
    end: string;
  };

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

export interface FeedbackVote {
  user_id: string;
  vote: "up" | "down";
  created_at?: string;
}

export interface FeedbackSentiment {
  overall:
    | "positive"
    | "neutral"
    | "negative"
    | "mixed"
    | "unknown";

  positive: number;
  neutral: number;
  negative: number;

  summary: string | null;
  key_points: string[];
}

export interface FeedbackMessage {
  message_id: string;
  user_id: string;
  username: string;
  content: string;
  created_at: string;
}

export interface CommunityFeedback {
  _id: string;

  feedback_id?: string;

  suggestion: string;

  author_id: string;
  author_name: string;

  channel_id?: string;
  message_id?: string;
  thread_id?: string;

  votes: FeedbackVote[];

  upvotes: number;
  downvotes: number;

  discussion: {
    message_count: number;
    messages: FeedbackMessage[];

    sentiment: FeedbackSentiment;
  };

  status: string;

  source?: string;

  created_at: string;
  updated_at: string;

  score: number;
}