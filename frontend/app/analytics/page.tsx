"use client";

import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  BookOpen,
  CheckCircle2,
  FileQuestion,
  RefreshCw,
  TrendingUp,
  Users,
} from "lucide-react";

import {
  getAnalyticsActivity,
  getAnalyticsKnowledge,
  getAnalyticsOverview,
  getAnalyticsTopics,
  getCommunitySignals,
  refreshCommunitySignals,
} from "@/lib/api";

import type {
  AnalyticsActivity,
  AnalyticsKnowledge,
  AnalyticsOverview,
  AnalyticsTopic,
  CommunitySignal,
} from "@/types/api";

import InsightCard from "@/components/dashboard/InsightCard";

export default function AnalyticsPage() {
  const [overview, setOverview] =
    useState<AnalyticsOverview | null>(null);

  const [activity, setActivity] =
    useState<AnalyticsActivity[]>([]);

  const [topics, setTopics] =
    useState<AnalyticsTopic[]>([]);

  const [knowledge, setKnowledge] =
    useState<AnalyticsKnowledge | null>(null);

  const [signals, setSignals] =
    useState<CommunitySignal[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [refreshing, setRefreshing] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  async function loadAnalytics() {
    try {
      setError(null);

      const [
        overviewData,
        activityData,
        topicsData,
        knowledgeData,
        signalsData,
      ] = await Promise.all([
        getAnalyticsOverview(),
        getAnalyticsActivity(30),
        getAnalyticsTopics(),
        getAnalyticsKnowledge(30),
        getCommunitySignals(),
      ]);

      setOverview(overviewData);
      setActivity(activityData);
      setTopics(topicsData);
      setKnowledge(knowledgeData);
      setSignals(signalsData);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load analytics.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleRefreshSignals() {
    try {
      setRefreshing(true);

      const result =
        await refreshCommunitySignals();

      setSignals(result.insights);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to refresh insights.",
      );
    } finally {
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 w-40 rounded-lg bg-zinc-200" />

          <div className="mt-2 h-4 w-72 rounded bg-zinc-100" />

          <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {Array.from({ length: 4 }).map(
              (_, index) => (
                <div
                  key={index}
                  className="h-32 rounded-2xl bg-zinc-100"
                />
              ),
            )}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="rounded-2xl border border-red-200 bg-red-50 p-5">
          <h2 className="font-semibold text-red-900">
            Failed to load analytics
          </h2>

          <p className="mt-1 text-sm text-red-700">
            {error}
          </p>

          <button
            onClick={loadAnalytics}
            className="mt-4 rounded-lg bg-red-900 px-4 py-2 text-sm font-medium text-white hover:bg-red-800"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-full bg-zinc-50 p-6 lg:p-8">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-zinc-950">
            Analytics
          </h1>

          <p className="mt-1 text-sm text-zinc-500">
            Understand community activity, resolution,
            knowledge coverage, and emerging needs.
          </p>
        </div>

        <button
          onClick={handleRefreshSignals}
          disabled={refreshing}
          className="inline-flex w-fit items-center gap-2 rounded-xl border border-zinc-200 bg-white px-4 py-2.5 text-sm font-medium text-zinc-900 shadow-sm transition hover:border-zinc-300 hover:bg-zinc-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <RefreshCw
            size={15}
            className={
              refreshing
                ? "animate-spin"
                : ""
            }
          />

          {refreshing
            ? "Refreshing..."
            : "Refresh Insights"}
        </button>
      </div>

      {overview && (
        <section className="mt-8">
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <MetricCard
              title="Total Questions"
              value={overview.total_questions}
              icon={FileQuestion}
            />

            <MetricCard
              title="Resolved"
              value={overview.resolved}
              icon={CheckCircle2}
              detail={`${overview.resolution_rate}% resolution rate`}
            />

            <MetricCard
              title="Knowledge Found"
              value={overview.knowledge_found}
              icon={BookOpen}
              detail={`${overview.knowledge_coverage_rate}% coverage`}
            />

            <MetricCard
              title="Sarvam Fallback"
              value={overview.sarvam_fallback}
              icon={ArrowUpRight}
              detail={`${overview.fallback_rate}% fallback rate`}
            />
          </div>
        </section>
      )}

      <section className="mt-8 grid gap-5 xl:grid-cols-3">
        {/* Activity */}
        <div className="xl:col-span-2 rounded-2xl border border-zinc-200 bg-white p-5">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-semibold text-zinc-950">
                Community Activity
              </h2>

              <p className="mt-1 text-xs text-zinc-500">
                Activity over the last 30 days
              </p>
            </div>

            <Activity
              size={18}
              className="text-zinc-400"
            />
          </div>

          <div className="mt-6 space-y-3">
            {activity.length === 0 ? (
              <EmptyState text="No activity recorded yet." />
            ) : (
              activity.map((item) => (
                <ActivityRow
                  key={item.date}
                  activity={item}
                />
              ))
            )}
          </div>
        </div>

        {overview && (
          <div className="rounded-2xl border border-zinc-200 bg-white p-5">
            <h2 className="font-semibold text-zinc-950">
              Resolution Health
            </h2>

            <p className="mt-1 text-xs text-zinc-500">
              How effectively CommunityOS is answering
              questions.
            </p>

            <div className="mt-6 space-y-5">
              <ProgressMetric
                label="Resolution Rate"
                value={overview.resolution_rate}
              />

              <ProgressMetric
                label="Knowledge Coverage"
                value={
                  overview.knowledge_coverage_rate
                }
              />

              <ProgressMetric
                label="Fallback Rate"
                value={overview.fallback_rate}
              />
            </div>

            <div className="mt-6 grid grid-cols-2 gap-3">
              <MiniMetric
                label="Escalated"
                value={overview.escalated}
              />

              <MiniMetric
                label="Fallback"
                value={overview.sarvam_fallback}
              />
            </div>
          </div>
        )}
      </section>

      <section className="mt-8 rounded-2xl border border-zinc-200 bg-white">
        <div className="border-b border-zinc-100 p-5">
          <div className="flex items-center gap-2">
            <TrendingUp
              size={18}
              className="text-zinc-500"
            />

            <h2 className="font-semibold text-zinc-950">
              Topic Analytics
            </h2>
          </div>

          <p className="mt-1 text-xs text-zinc-500">
            Questions and resolution performance by
            topic.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-zinc-100 text-xs text-zinc-500">
                <th className="px-5 py-3 font-medium">
                  Topic
                </th>

                <th className="px-5 py-3 font-medium">
                  Questions
                </th>

                <th className="px-5 py-3 font-medium">
                  Resolved
                </th>

                <th className="px-5 py-3 font-medium">
                  Knowledge
                </th>

                <th className="px-5 py-3 font-medium">
                  Fallback
                </th>

                <th className="px-5 py-3 font-medium">
                  Resolution
                </th>
              </tr>
            </thead>

            <tbody>
              {topics.map((topic) => (
                <TopicRow
                  key={topic.topic}
                  topic={topic}
                />
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {knowledge && (
        <section className="mt-8">
          <div className="mb-4">
            <h2 className="font-semibold text-zinc-950">
              Knowledge Base
            </h2>

            <p className="mt-1 text-xs text-zinc-500">
              Knowledge growth and candidate review
              pipeline.
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            <KnowledgeMetric
              label="Total Knowledge"
              value={knowledge.knowledge.total}
              icon={BookOpen}
            />

            <KnowledgeMetric
              label="Official"
              value={knowledge.knowledge.official}
            />

            <KnowledgeMetric
              label="Generated"
              value={knowledge.knowledge.generated}
            />

            <KnowledgeMetric
              label="Pending Candidates"
              value={knowledge.candidates.pending}
              icon={AlertTriangle}
            />

            <KnowledgeMetric
              label="Approved Candidates"
              value={knowledge.candidates.approved}
              icon={CheckCircle2}
            />
          </div>
        </section>
      )}

      <section className="mt-8">
        <div className="mb-4 flex items-end justify-between">
          <div>
            <h2 className="font-semibold text-zinc-950">
              Community Insights
            </h2>

            <p className="mt-1 text-xs text-zinc-500">
              Signals detected from community activity.
            </p>
          </div>

          <span className="text-xs text-zinc-400">
            {signals.length} signals
          </span>
        </div>

        {signals.length === 0 ? (
          <div className="rounded-2xl border border-zinc-200 bg-white p-8 text-center">
            <LightbulbPlaceholder />

            <p className="mt-3 text-sm text-zinc-500">
              No community signals detected.
            </p>
          </div>
        ) : (
          <div className="grid gap-4 lg:grid-cols-2">
            {signals.map((signal, index) => (
              <InsightCard
                key={`${signal.type}-${signal.created_at}-${index}`}
                insight={signal}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function MetricCard({
  title,
  value,
  icon: Icon,
  detail,
}: {
  title: string;
  value: number;
  icon: typeof Activity;
  detail?: string;
}) {
  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-5">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-zinc-500">
          {title}
        </span>

        <Icon
          size={17}
          className="text-zinc-400"
        />
      </div>

      <div className="mt-3 text-2xl font-semibold tracking-tight text-zinc-950">
        {value}
      </div>

      {detail && (
        <p className="mt-1 text-xs text-zinc-400">
          {detail}
        </p>
      )}
    </div>
  );
}

function ActivityRow({
  activity,
}: {
  activity: AnalyticsActivity;
}) {
  const total =
    activity.questions +
    activity.messages;

  const questionPercentage =
    total > 0
      ? (activity.questions / total) * 100
      : 0;

  return (
    <div className="rounded-xl bg-zinc-50 p-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-zinc-700">
          {formatDate(activity.date)}
        </span>

        <span className="text-xs text-zinc-400">
          {activity.messages} messages
        </span>
      </div>

      <div className="mt-3 h-2 overflow-hidden rounded-full bg-zinc-200">
        <div
          className="h-full rounded-full bg-zinc-800"
          style={{
            width: `${Math.min(
              questionPercentage,
              100,
            )}%`,
          }}
        />
      </div>

      <div className="mt-2 flex flex-wrap gap-3 text-[11px] text-zinc-500">
        <span>
          {activity.questions} questions
        </span>

        <span>
          {activity.resolved} resolved
        </span>

        <span>
          {activity.fallback} fallback
        </span>

        <span>
          {activity.escalated} escalated
        </span>
      </div>
    </div>
  );
}

function TopicRow({
  topic,
}: {
  topic: AnalyticsTopic;
}) {
  return (
    <tr className="border-b border-zinc-100 last:border-0">
      <td className="px-5 py-4">
        <span className="rounded-lg bg-zinc-100 px-2.5 py-1 text-xs font-medium text-zinc-700">
          #{topic.topic}
        </span>
      </td>

      <td className="px-5 py-4 text-sm text-zinc-700">
        {topic.questions}
      </td>

      <td className="px-5 py-4 text-sm text-zinc-700">
        {topic.resolved}
      </td>

      <td className="px-5 py-4 text-sm text-zinc-700">
        {topic.knowledge_found}
      </td>

      <td className="px-5 py-4 text-sm text-zinc-700">
        {topic.sarvam_fallback}
      </td>

      <td className="px-5 py-4">
        <span
          className={`text-sm font-medium ${
            topic.resolution_rate >= 80
              ? "text-emerald-600"
              : topic.resolution_rate >= 50
                ? "text-amber-600"
                : "text-red-600"
          }`}
        >
          {topic.resolution_rate}%
        </span>
      </td>
    </tr>
  );
}

function ProgressMetric({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div>
      <div className="flex items-center justify-between text-xs">
        <span className="text-zinc-500">
          {label}
        </span>

        <span className="font-medium text-zinc-900">
          {value}%
        </span>
      </div>

      <div className="mt-2 h-2 overflow-hidden rounded-full bg-zinc-100">
        <div
          className="h-full rounded-full bg-zinc-900 transition-all"
          style={{
            width: `${Math.min(
              Math.max(value, 0),
              100,
            )}%`,
          }}
        />
      </div>
    </div>
  );
}

function MiniMetric({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="rounded-xl border border-zinc-200 p-3">
      <p className="text-[11px] text-zinc-400">
        {label}
      </p>

      <p className="mt-1 text-lg font-semibold text-zinc-950">
        {value}
      </p>
    </div>
  );
}

function KnowledgeMetric({
  label,
  value,
  icon: Icon,
}: {
  label: string;
  value: number;
  icon?: typeof BookOpen;
}) {
  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-5">
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium text-zinc-500">
          {label}
        </p>

        {Icon && (
          <Icon
            size={16}
            className="text-zinc-400"
          />
        )}
      </div>

      <p className="mt-3 text-2xl font-semibold tracking-tight text-zinc-950">
        {value}
      </p>
    </div>
  );
}

function EmptyState({
  text,
}: {
  text: string;
}) {
  return (
    <div className="rounded-xl border border-dashed border-zinc-200 p-6 text-center">
      <p className="text-sm text-zinc-400">
        {text}
      </p>
    </div>
  );
}


function LightbulbPlaceholder() {
  return (
    <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl bg-zinc-100">
      <TrendingUp
        size={18}
        className="text-zinc-400"
      />
    </div>
  );
}

function formatDate(date: string) {
  return new Date(
    `${date}T00:00:00`,
  ).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}