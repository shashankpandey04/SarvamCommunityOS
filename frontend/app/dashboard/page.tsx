"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { apiFetch } from "@/lib/api";
import type {
  CommunityOverview,
  CommunitySignal,
  TrendingTopic,
} from "@/types/api";

export default function DashboardPage() {
  const [overview, setOverview] =
    useState<CommunityOverview | null>(null);

  const [trends, setTrends] =
    useState<TrendingTopic[]>([]);

  const [signals, setSignals] =
    useState<CommunitySignal[]>([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError(null);

        const [
          overviewData,
          trendsData,
          signalsData,
        ] = await Promise.all([
          apiFetch<CommunityOverview>(
            "/api/community/overview"
          ),
          apiFetch<TrendingTopic[]>(
            "/api/community/trends"
          ),
          apiFetch<CommunitySignal[]>(
            "/api/community/signals"
          ),
        ]);

        setOverview(overviewData);
        setTrends(trendsData);
        setSignals(signalsData);
      } catch (error) {
        console.error(error);
        setError("Unable to load community overview.");
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  if (loading) {
    return <OverviewSkeleton />;
  }

  if (!overview || error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6">
        <h2 className="text-sm font-semibold text-red-900">
          Unable to load overview
        </h2>

        <p className="mt-1 text-sm text-red-700">
          {error ?? "Something went wrong."}
        </p>
      </div>
    );
  }

  const topSignal = signals[0];
  const topTopic = trends[0];

  return (
    <div className="space-y-8">

      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-950">
          Community Overview
        </h1>

        <p className="mt-1 text-sm text-zinc-500">
          A quick look at the health and activity of your
          community.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">

        <MetricCard
          label="Members"
          value={overview.members}
          description="Community members"
        />

        <MetricCard
          label="Messages"
          value={overview.messages}
          description="Messages processed"
        />

        <MetricCard
          label="Questions"
          value={overview.questions}
          description="Questions identified"
        />

        <MetricCard
          label="Resolution Rate"
          value={`${overview.resolution_rate}%`}
          description={`${overview.resolved} resolved`}
        />

      </div>

      <div className="grid gap-6 lg:grid-cols-2">

        <section className="rounded-xl border border-zinc-200 bg-white">

          <div className="border-b border-zinc-200 px-6 py-5">

            <h2 className="text-sm font-semibold text-zinc-950">
              Community Health
            </h2>

            <p className="mt-1 text-xs text-zinc-500">
              Current support health at a glance.
            </p>

          </div>

          <div className="grid grid-cols-2 gap-px bg-zinc-100">

            <HealthStat
              label="Questions"
              value={overview.questions}
            />

            <HealthStat
              label="Resolved"
              value={overview.resolved}
            />

            <HealthStat
              label="Escalated"
              value={overview.escalated}
            />

            <HealthStat
              label="Resolution"
              value={`${overview.resolution_rate}%`}
            />

          </div>

        </section>

        <section className="rounded-xl border border-zinc-200 bg-white">

          <div className="border-b border-zinc-200 px-6 py-5">

            <h2 className="text-sm font-semibold text-zinc-950">
              Attention Needed
            </h2>

            <p className="mt-1 text-xs text-zinc-500">
              The most important signal right now.
            </p>

          </div>

          <div className="p-6">

            {topSignal ? (
              <div>

                <div className="flex items-start justify-between gap-4">

                  <div>
                    <p className="text-sm font-semibold text-zinc-950">
                      {topSignal.title}
                    </p>

                    <p className="mt-2 text-sm leading-6 text-zinc-600">
                      {topSignal.message}
                    </p>
                  </div>

                  <SeverityBadge
                    severity={topSignal.severity}
                  />

                </div>

                {topSignal.suggestion && (
                  <div className="mt-4 rounded-lg bg-zinc-50 p-3">

                    <p className="text-xs leading-5 text-zinc-600">
                      <span className="font-medium text-zinc-800">
                        Recommendation:
                      </span>{" "}
                      {topSignal.suggestion}
                    </p>

                  </div>
                )}

              </div>
            ) : (
              <div className="py-4 text-sm text-zinc-500">
                No immediate issues detected.
              </div>
            )}

          </div>

        </section>

      </div>

      <section className="rounded-xl border border-zinc-200 bg-white">

        <div className="border-b border-zinc-200 px-6 py-5">

          <h2 className="text-sm font-semibold text-zinc-950">
            Community Snapshot
          </h2>

          <p className="mt-1 text-xs text-zinc-500">
            A couple of things worth knowing right now.
          </p>

        </div>

        <div className="grid gap-0 md:grid-cols-2">

          <div className="border-b border-zinc-100 p-6 md:border-b-0 md:border-r">

            <p className="text-xs font-medium uppercase tracking-wide text-zinc-400">
              Top Topic
            </p>

            {topTopic ? (
              <>

                <p className="mt-3 text-xl font-semibold text-zinc-950">
                  {topTopic.topic || "General"}
                </p>

                <p className="mt-1 text-sm text-zinc-500">
                  {topTopic.mentions} mentions
                </p>

              </>
            ) : (
              <p className="mt-3 text-sm text-zinc-500">
                No topic data available.
              </p>
            )}

          </div>

          <div className="p-6">

            <p className="text-xs font-medium uppercase tracking-wide text-zinc-400">
              Support Attention
            </p>

            <p className="mt-3 text-xl font-semibold text-zinc-950">
              {overview.escalated}
            </p>

            <p className="mt-1 text-sm text-zinc-500">
              escalated questions need attention
            </p>

          </div>

        </div>

      </section>

      {signals.length > 0 && (
        <section className="rounded-xl border border-zinc-200 bg-white">

          <div className="flex items-center justify-between border-b border-zinc-200 px-6 py-5">

            <div>
              <h2 className="text-sm font-semibold text-zinc-950">
                Recent Signals
              </h2>

              <p className="mt-1 text-xs text-zinc-500">
                Recommendations generated by CommunityOS.
              </p>
            </div>

            <Link
              href="/analytics"
              className="text-xs font-medium text-zinc-600 hover:text-zinc-950"
            >
              View analytics →
            </Link>

          </div>

          <div className="divide-y divide-zinc-100">

            {signals.slice(0, 3).map((signal, index) => (
              <SignalPreview
                key={`${signal.type}-${index}`}
                signal={signal}
              />
            ))}

          </div>

        </section>
      )}

    </div>
  );
}

function MetricCard({
  label,
  value,
  description,
}: {
  label: string;
  value: string | number;
  description: string;
}) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-5">

      <p className="text-sm font-medium text-zinc-500">
        {label}
      </p>

      <p className="mt-3 text-3xl font-semibold tracking-tight text-zinc-950">
        {value}
      </p>

      <p className="mt-2 text-xs text-zinc-500">
        {description}
      </p>

    </div>
  );
}

function HealthStat({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="bg-white p-5">

      <p className="text-xs text-zinc-500">
        {label}
      </p>

      <p className="mt-2 text-xl font-semibold text-zinc-950">
        {value}
      </p>

    </div>
  );
}

function SeverityBadge({
  severity,
}: {
  severity: string;
}) {
  return (
    <span className="shrink-0 rounded-full bg-zinc-100 px-2.5 py-1 text-[10px] font-medium uppercase tracking-wide text-zinc-600">
      {severity}
    </span>
  );
}

function SignalPreview({
  signal,
}: {
  signal: CommunitySignal;
}) {
  return (
    <div className="flex items-start gap-4 px-6 py-4">

      <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-zinc-100">

        <span className="h-2 w-2 rounded-full bg-zinc-500" />

      </div>

      <div className="min-w-0 flex-1">

        <div className="flex flex-wrap items-center gap-2">

          <p className="text-sm font-medium text-zinc-950">
            {signal.title}
          </p>

          <SeverityBadge
            severity={signal.severity}
          />

        </div>

        <p className="mt-1 text-sm text-zinc-600">
          {signal.message}
        </p>

      </div>

    </div>
  );
}

function OverviewSkeleton() {
  return (
    <div className="space-y-8">

      <div className="space-y-2">
        <div className="h-7 w-48 animate-pulse rounded bg-zinc-200" />
        <div className="h-4 w-80 animate-pulse rounded bg-zinc-200" />
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {[1, 2, 3, 4].map((item) => (
          <div
            key={item}
            className="h-32 animate-pulse rounded-xl border border-zinc-200 bg-white"
          />
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">

        <div className="h-64 animate-pulse rounded-xl border border-zinc-200 bg-white" />

        <div className="h-64 animate-pulse rounded-xl border border-zinc-200 bg-white" />

      </div>

    </div>
  );
}