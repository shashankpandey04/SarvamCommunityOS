"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

type AnalyticsOverview = {
  total_questions: number;
  resolved: number;
  escalated: number;
  knowledge_found: number;
  sarvam_fallback: number;
  resolution_rate: number;
  knowledge_coverage_rate: number;
  fallback_rate: number;
};

type ActivityItem = {
  date: string;
  messages: number;
  questions: number;
  resolved: number;
  escalated: number;
  fallback: number;
};

type TopicItem = {
  topic: string;
  questions: number;
  resolved: number;
  escalated: number;
  knowledge_found: number;
  sarvam_fallback: number;
  resolution_rate: number;
};

type KnowledgeAnalytics = {
  period: {
    days: number;
    start: string;
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
};

type AnalyticsData = {
  overview: AnalyticsOverview | null;
  activity: ActivityItem[];
  topics: TopicItem[];
  knowledge: KnowledgeAnalytics | null;
};

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData>({
    overview: null,
    activity: [],
    topics: [],
    knowledge: null,
  });

  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadAnalytics() {
    try {
      setLoading(true);
      setError(null);

      const [
        overview,
        activity,
        topics,
        knowledge,
      ] = await Promise.all([
        apiFetch<AnalyticsOverview>(
          "/api/analytics/overview"
        ),

        apiFetch<ActivityItem[]>(
          `/api/analytics/activity?days=${days}`
        ),

        apiFetch<TopicItem[]>(
          "/api/analytics/topics"
        ),

        apiFetch<KnowledgeAnalytics>(
          `/api/analytics/knowledge?days=${days}`
        ),
      ]);

      setData({
        overview,
        activity,
        topics,
        knowledge,
      });
    } catch (error) {
      console.error(
        "Failed to load analytics:",
        error
      );

      setError(
        "Unable to load analytics data."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAnalytics();
  }, [days]);

  if (loading) {
    return <AnalyticsSkeleton />;
  }

  if (error) {
    return (
      <div className="space-y-6">

        <PageHeader />

        <div className="rounded-xl border border-red-200 bg-red-50 p-5">
          <p className="text-sm text-red-700">
            {error}
          </p>
        </div>

        <button
          onClick={loadAnalytics}
          className="rounded-lg border border-zinc-200 bg-white px-4 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-50"
        >
          Try again
        </button>

      </div>
    );
  }

  const overview = data.overview;
  const knowledge = data.knowledge;

  return (
    <div className="space-y-8">

      {/* =================================================
          Header
      ================================================= */}

      <PageHeader
        days={days}
        onDaysChange={setDays}
        onRefresh={loadAnalytics}
      />


      {/* =================================================
          Overview
      ================================================= */}

      {overview && (
        <section>

          <SectionTitle
            title="Community Performance"
            description="How effectively the community is getting answers."
          />

          <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

            <MetricCard
              label="Questions"
              value={overview.total_questions}
            />

            <MetricCard
              label="Resolved"
              value={overview.resolved}
              suffix={`${overview.resolution_rate}% resolution`}
            />

            <MetricCard
              label="Knowledge Found"
              value={overview.knowledge_found}
              suffix={`${overview.knowledge_coverage_rate}% coverage`}
            />

            <MetricCard
              label="Sarvam Fallback"
              value={overview.sarvam_fallback}
              suffix={`${overview.fallback_rate}% fallback`}
            />

          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2">

            <MetricCard
              label="Escalated"
              value={overview.escalated}
            />

            <MetricCard
              label="Unresolved"
              value={
                Math.max(
                  overview.total_questions -
                    overview.resolved,
                  0
                )
              }
            />

          </div>

        </section>
      )}


      {/* =================================================
          Activity
      ================================================= */}

      <section className="rounded-xl border border-zinc-200 bg-white">

        <SectionHeader
          title="Activity Over Time"
          description={`Community activity during the last ${days} days.`}
        />

        <div className="p-6">

          {data.activity.length > 0 ? (
            <ActivityChart
              activity={data.activity}
            />
          ) : (
            <EmptyState
              message="No activity recorded for this period."
            />
          )}

        </div>

      </section>


      {/* =================================================
          Topic Intelligence
      ================================================= */}

      <section className="rounded-xl border border-zinc-200 bg-white">

        <SectionHeader
          title="Topic Intelligence"
          description="Understand which topics are generating questions and where knowledge is helping."
        />

        <div className="overflow-x-auto">

          <table className="w-full text-left">

            <thead>
              <tr className="border-b border-zinc-200 text-xs text-zinc-400">

                <th className="px-6 py-4 font-medium">
                  Topic
                </th>

                <th className="px-6 py-4 font-medium">
                  Questions
                </th>

                <th className="px-6 py-4 font-medium">
                  Resolved
                </th>

                <th className="px-6 py-4 font-medium">
                  Knowledge
                </th>

                <th className="px-6 py-4 font-medium">
                  Fallback
                </th>

                <th className="px-6 py-4 font-medium">
                  Resolution
                </th>

              </tr>
            </thead>

            <tbody className="divide-y divide-zinc-100">

              {data.topics.map((topic) => (
                <TopicRow
                  key={topic.topic}
                  topic={topic}
                />
              ))}

            </tbody>

          </table>

        </div>

      </section>


      {/* =================================================
          Knowledge Analytics
      ================================================= */}

      {knowledge && (
        <section>

          <SectionTitle
            title="Knowledge Base"
            description="Knowledge coverage and candidate pipeline for the selected period."
          />

          <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">

            <MetricCard
              label="Total Knowledge"
              value={
                knowledge.knowledge.total
              }
            />

            <MetricCard
              label="Official"
              value={
                knowledge.knowledge.official
              }
            />

            <MetricCard
              label="Generated"
              value={
                knowledge.knowledge.generated
              }

            />

          </div>


          <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

            <MetricCard
              label="Candidates"
              value={
                knowledge.candidates.total
              }
            />

            <MetricCard
              label="Pending"
              value={
                knowledge.candidates.pending
              }
            />

            <MetricCard
              label="Approved"
              value={
                knowledge.candidates.approved
              }
            />

            <MetricCard
              label="Rejected"
              value={
                knowledge.candidates.rejected
              }
            />

          </div>

        </section>
      )}

    </div>
  );
}


/* =========================================================
   Header
========================================================= */

function PageHeader({
  days,
  onDaysChange,
  onRefresh,
}: {
  days?: number;
  onDaysChange?: (days: number) => void;
  onRefresh?: () => void;
}) {
  return (
    <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">

      <div>

        <p className="text-xs font-medium uppercase tracking-wider text-zinc-400">
          Intelligence
        </p>

        <h1 className="mt-2 text-2xl font-semibold tracking-tight text-zinc-950">
          Analytics
        </h1>

        <p className="mt-1 text-sm text-zinc-500">
          Understand community activity,
          resolution, knowledge coverage,
          and support patterns.
        </p>

      </div>

      <div className="flex items-center gap-2">

        <select
          value={days}
          onChange={(event) =>
            onDaysChange?.(
              Number(event.target.value)
            )
          }
          className="rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-700 outline-none focus:border-zinc-400"
        >
          <option value={7}>
            Last 7 days
          </option>

          <option value={30}>
            Last 30 days
          </option>

          <option value={90}>
            Last 90 days
          </option>
        </select>

        <button
          onClick={onRefresh}
          className="rounded-lg border border-zinc-200 bg-white px-4 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-50"
        >
          Refresh
        </button>

      </div>

    </div>
  );
}


/* =========================================================
   Section Title
========================================================= */

function SectionTitle({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div>

      <h2 className="text-sm font-semibold text-zinc-950">
        {title}
      </h2>

      <p className="mt-1 text-xs text-zinc-500">
        {description}
      </p>

    </div>
  );
}


/* =========================================================
   Section Header
========================================================= */

function SectionHeader({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="border-b border-zinc-200 px-6 py-5">

      <h2 className="text-sm font-semibold text-zinc-950">
        {title}
      </h2>

      <p className="mt-1 text-xs text-zinc-500">
        {description}
      </p>

    </div>
  );
}


/* =========================================================
   Metric Card
========================================================= */

function MetricCard({
  label,
  value,
  suffix,
}: {
  label: string;
  value: string | number;
  suffix?: string;
}) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-5">

      <p className="text-sm font-medium text-zinc-500">
        {label}
      </p>

      <p className="mt-3 text-2xl font-semibold tracking-tight text-zinc-950">
        {value}
      </p>

      {suffix && (
        <p className="mt-2 text-xs text-zinc-400">
          {suffix}
        </p>
      )}

    </div>
  );
}


/* =========================================================
   Activity Chart
========================================================= */

function ActivityChart({
  activity,
}: {
  activity: ActivityItem[];
}) {
  const maxValue = Math.max(
    ...activity.map((item) =>
      Math.max(
        item.messages,
        item.questions,
        item.resolved,
        item.fallback
      )
    ),
    1
  );

  return (
    <div>

      <div className="flex h-64 items-end gap-1 border-b border-zinc-200">

        {activity.map((item) => {

          const height =
            (item.messages / maxValue) * 100;

          return (
            <div
              key={item.date}
              className="group relative flex h-full flex-1 items-end"
              title={`${item.date}: ${item.messages} messages`}
            >

              <div
                className="w-full rounded-t bg-zinc-900 transition-opacity group-hover:opacity-70"
                style={{
                  height: `${Math.max(
                    height,
                    1
                  )}%`,
                }}
              />

            </div>
          );
        })}

      </div>

      <div className="mt-3 flex justify-between text-[10px] text-zinc-400">

        <span>
          {activity[0]?.date}
        </span>

        <span>
          {activity[activity.length - 1]?.date}
        </span>

      </div>

      <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-5">

        <ActivityLegend
          label="Messages"
          value={sum(activity, "messages")}
        />

        <ActivityLegend
          label="Questions"
          value={sum(activity, "questions")}
        />

        <ActivityLegend
          label="Resolved"
          value={sum(activity, "resolved")}
        />

        <ActivityLegend
          label="Escalated"
          value={sum(activity, "escalated")}
        />

        <ActivityLegend
          label="Fallback"
          value={sum(activity, "fallback")}
        />

      </div>

    </div>
  );
}


/* =========================================================
   Activity Legend
========================================================= */

function ActivityLegend({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="rounded-lg bg-zinc-50 p-3">

      <p className="text-[11px] text-zinc-400">
        {label}
      </p>

      <p className="mt-1 text-sm font-semibold text-zinc-900">
        {value}
      </p>

    </div>
  );
}


/* =========================================================
   Topic Row
========================================================= */

function TopicRow({
  topic,
}: {
  topic: TopicItem;
}) {
  return (
    <tr className="text-sm">

      <td className="px-6 py-4 font-medium text-zinc-900">
        {topic.topic}
      </td>

      <td className="px-6 py-4 text-zinc-600">
        {topic.questions}
      </td>

      <td className="px-6 py-4 text-zinc-600">
        {topic.resolved}
      </td>

      <td className="px-6 py-4 text-zinc-600">
        {topic.knowledge_found}
      </td>

      <td className="px-6 py-4 text-zinc-600">
        {topic.sarvam_fallback}
      </td>

      <td className="px-6 py-4">

        <span
          className={`font-medium ${
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


/* =========================================================
   Empty State
========================================================= */

function EmptyState({
  message,
}: {
  message: string;
}) {
  return (
    <div className="py-12 text-center">

      <p className="text-sm text-zinc-500">
        {message}
      </p>

    </div>
  );
}


/* =========================================================
   Helpers
========================================================= */

function sum(
  items: ActivityItem[],
  key: keyof ActivityItem
) {
  return items.reduce(
    (total, item) =>
      total +
      (typeof item[key] === "number"
        ? item[key]
        : 0),
    0
  );
}


/* =========================================================
   Loading
========================================================= */

function AnalyticsSkeleton() {
  return (
    <div className="space-y-8">

      <div className="space-y-2">
        <div className="h-7 w-48 animate-pulse rounded bg-zinc-200" />
        <div className="h-4 w-96 animate-pulse rounded bg-zinc-200" />
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

        {[1, 2, 3, 4].map((item) => (
          <div
            key={item}
            className="h-32 animate-pulse rounded-xl border border-zinc-200 bg-white"
          />
        ))}

      </div>

      <div className="h-80 animate-pulse rounded-xl border border-zinc-200 bg-white" />

      <div className="h-72 animate-pulse rounded-xl border border-zinc-200 bg-white" />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">

        {[1, 2, 3].map((item) => (
          <div
            key={item}
            className="h-28 animate-pulse rounded-xl border border-zinc-200 bg-white"
          />
        ))}

      </div>

    </div>
  );
}