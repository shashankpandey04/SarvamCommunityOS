"use client";

import {
  FileQuestion,
  Lightbulb,
  TrendingUp,
} from "lucide-react";

import type { CommunityInsight } from "@/types/api";

interface InsightCardProps {
  insight: CommunityInsight;
}

function getInsightIcon(type: string) {
  switch (type) {
    case "trending_topic":
      return TrendingUp;

    case "repeated_question":
      return FileQuestion;

    default:
      return Lightbulb;
  }
}

export default function InsightCard({
  insight,
}: InsightCardProps) {
  const Icon = getInsightIcon(
    insight.type,
  );

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-5 transition hover:border-zinc-300 hover:shadow-sm">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex min-w-0 items-start gap-3">
          <div
            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${
              insight.severity === "critical"
                ? "bg-red-50 text-red-600"
                : insight.severity === "high"
                  ? "bg-orange-50 text-orange-600"
                  : insight.severity === "medium"
                    ? "bg-amber-50 text-amber-600"
                    : "bg-zinc-100 text-zinc-600"
            }`}
          >
            <Icon size={19} />
          </div>

          <div className="min-w-0">
            <h3 className="text-sm font-semibold text-zinc-950">
              {insight.title}
            </h3>

            <p className="mt-1 text-sm leading-6 text-zinc-500">
              {insight.message}
            </p>
          </div>
        </div>

        <span className="shrink-0 rounded-full bg-zinc-100 px-2 py-1 text-[10px] font-medium uppercase tracking-wide text-zinc-500">
          {insight.severity}
        </span>
      </div>

      {/* Repeated Question */}
      {insight.metric?.question && (
        <div className="mt-4 rounded-xl border border-zinc-200 bg-zinc-50 p-4">
          <div className="flex items-center gap-2">
            <FileQuestion
              size={14}
              className="text-zinc-400"
            />

            <span className="text-[11px] font-medium uppercase tracking-wide text-zinc-400">
              Community Question
            </span>
          </div>

          <p className="mt-2 text-sm font-medium leading-6 text-zinc-800">
            {insight.metric.question}
          </p>
        </div>
      )}

      {/* Suggestion */}
      {insight.suggestion && (
        <div className="mt-4 rounded-xl bg-zinc-50 p-3">
          <div className="flex gap-2">
            <Lightbulb
              size={15}
              className="mt-0.5 shrink-0 text-zinc-500"
            />

            <p className="text-xs leading-5 text-zinc-600">
              {insight.suggestion}
            </p>
          </div>
        </div>
      )}

      {/* Metrics */}
      {(insight.metric || insight.topic) && (
        <div className="mt-4 flex flex-wrap gap-2">
          {insight.metric?.current_questions !==
            undefined && (
            <span className="rounded-lg border border-zinc-200 px-2.5 py-1 text-xs text-zinc-500">
              {insight.metric.current_questions} questions
            </span>
          )}

          {insight.metric?.previous_questions !==
            undefined && (
            <span className="rounded-lg border border-zinc-200 px-2.5 py-1 text-xs text-zinc-500">
              {insight.metric.previous_questions} previous
            </span>
          )}

          {insight.metric?.growth_percent !==
            undefined && (
            <span className="rounded-lg border border-zinc-200 px-2.5 py-1 text-xs text-zinc-500">
              {insight.metric.growth_percent}% growth
            </span>
          )}

          {insight.metric?.occurrences !==
            undefined && (
            <span className="rounded-lg border border-zinc-200 px-2.5 py-1 text-xs text-zinc-500">
              {insight.metric.occurrences} occurrences
            </span>
          )}

          {insight.topic && (
            <span className="rounded-lg border border-zinc-200 px-2.5 py-1 text-xs text-zinc-500">
              #{insight.topic}
            </span>
          )}
        </div>
      )}

      {/* Recommendation */}
      {insight.suggestion && (
        <div className="mt-5 border-t border-zinc-100 pt-4">
          <p className="text-[11px] font-medium uppercase tracking-wide text-zinc-400">
            Recommended Action
          </p>

          <p className="mt-1 text-xs leading-5 text-zinc-600">
            {insight.suggestion}
          </p>
        </div>
      )}
    </div>
  );
}