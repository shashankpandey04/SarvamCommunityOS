"use client";

import { useEffect, useMemo, useState } from "react";

import {
  ChevronDown,
  ChevronUp,
  MessageSquare,
  Search,
  ThumbsDown,
  ThumbsUp,
  TrendingUp,
} from "lucide-react";

import type {
  CommunityFeedback,
} from "@/types/api";

import {
  getFeedback,
  getTopFeedback,
} from "@/lib/api";


// ============================================================
// Helpers
// ============================================================

function sentimentLabel(
  sentiment: string,
) {
  switch (sentiment) {
    case "positive":
      return "Positive";

    case "negative":
      return "Negative";

    case "neutral":
      return "Neutral";

    case "mixed":
      return "Mixed";

    default:
      return "Unknown";
  }
}


function sentimentClass(
  sentiment: string,
) {
  switch (sentiment) {
    case "positive":
      return "bg-emerald-50 text-emerald-700";

    case "negative":
      return "bg-red-50 text-red-700";

    case "neutral":
      return "bg-zinc-100 text-zinc-600";

    case "mixed":
      return "bg-amber-50 text-amber-700";

    default:
      return "bg-zinc-100 text-zinc-500";
  }
}


function statusClass(
  status: string,
) {
  switch (status) {
    case "open":
      return "bg-blue-50 text-blue-700";

    case "actionable":
      return "bg-emerald-50 text-emerald-700";

    case "reviewed":
      return "bg-amber-50 text-amber-700";

    default:
      return "bg-zinc-100 text-zinc-500";
  }
}


// ============================================================
// Feedback Card
// ============================================================

function FeedbackCard({
  feedback,
}: {
  feedback: CommunityFeedback;
}) {
  const [expanded, setExpanded] =
    useState(false);

  const sentiment =
    feedback.discussion?.sentiment ?? {
      overall: "unknown",
      positive: 0,
      neutral: 0,
      negative: 0,
      summary: null,
      key_points: [],
    };

  return (
    <div className="overflow-hidden rounded-2xl border border-zinc-200 bg-white">

      {/* =====================================================
          Main Feedback
      ===================================================== */}

      <button
        type="button"
        onClick={() =>
          setExpanded(
            (value) => !value,
          )
        }
        className="w-full p-5 text-left transition hover:bg-zinc-50"
      >
        <div className="flex items-start gap-4">

          {/* Vote score */}

          <div className="flex w-16 shrink-0 flex-col items-center rounded-xl border border-zinc-200 px-2 py-3">

            <ThumbsUp
              size={15}
              className="text-zinc-400"
            />

            <span className="mt-1 text-xl font-semibold text-zinc-950">
              {feedback.upvotes}
            </span>

            <span className="text-[10px] text-zinc-400">
              upvotes
            </span>

          </div>


          {/* Feedback content */}

          <div className="min-w-0 flex-1">

            {/* Metadata */}

            <div className="flex flex-wrap items-center gap-2">

              {feedback.source && (
                <span className="rounded-full bg-zinc-100 px-2.5 py-1 text-[10px] font-medium uppercase tracking-wide text-zinc-500">
                  {feedback.source}
                </span>
              )}

              <span
                className={`rounded-full px-2.5 py-1 text-[10px] font-medium capitalize ${statusClass(
                  feedback.status,
                )}`}
              >
                {feedback.status}
              </span>

            </div>


            {/* Suggestion */}

            <p className="mt-3 text-sm font-semibold leading-6 text-zinc-900">
              {feedback.suggestion}
            </p>


            {/* Author */}

            <p className="mt-1 text-xs text-zinc-400">
              Suggested by{" "}
              <span className="font-medium text-zinc-600">
                {feedback.author_name}
              </span>
            </p>


            {/* Metrics */}

            <div className="mt-4 flex flex-wrap items-center gap-4 text-xs text-zinc-400">

              <span className="flex items-center gap-1.5">
                <ThumbsUp size={13} />
                {feedback.upvotes}
              </span>

              <span className="flex items-center gap-1.5">
                <ThumbsDown size={13} />
                {feedback.downvotes}
              </span>

              <span className="flex items-center gap-1.5">
                <MessageSquare
                  size={13}
                />

                {
                  feedback.discussion
                    ?.message_count ?? 0
                }
              </span>

              <span
                className={`rounded-full px-2.5 py-1 ${sentimentClass(
                  sentiment.overall,
                )}`}
              >
                {sentimentLabel(
                  sentiment.overall,
                )}
              </span>

            </div>

          </div>


          {/* Expand */}

          <div className="pt-1 text-zinc-400">

            {expanded ? (
              <ChevronUp size={18} />
            ) : (
              <ChevronDown size={18} />
            )}

          </div>

        </div>
      </button>


      {/* =====================================================
          Expanded Details
      ===================================================== */}

      {expanded && (
        <div className="border-t border-zinc-100 px-5 pb-5">

          <div className="grid gap-4 pt-5 lg:grid-cols-2">

            {/* =================================================
                Sentiment
            ================================================= */}

            <div className="rounded-xl bg-zinc-50 p-4">

              <div className="flex items-center justify-between">

                <h3 className="text-xs font-semibold uppercase tracking-wide text-zinc-400">
                  Community Sentiment
                </h3>

                <span
                  className={`rounded-full px-2.5 py-1 text-[10px] font-medium ${sentimentClass(
                    sentiment.overall,
                  )}`}
                >
                  {sentimentLabel(
                    sentiment.overall,
                  )}
                </span>

              </div>


              {/* Positive */}

              <div className="mt-4">

                <div className="flex justify-between text-xs">

                  <span className="text-zinc-500">
                    Positive
                  </span>

                  <span className="font-medium text-zinc-700">
                    {sentiment.positive}%
                  </span>

                </div>

                <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-zinc-200">

                  <div
                    className="h-full rounded-full bg-emerald-500"
                    style={{
                      width: `${sentiment.positive}%`,
                    }}
                  />

                </div>

              </div>


              {/* Neutral */}

              <div className="mt-3">

                <div className="flex justify-between text-xs">

                  <span className="text-zinc-500">
                    Neutral
                  </span>

                  <span className="font-medium text-zinc-700">
                    {sentiment.neutral}%
                  </span>

                </div>

                <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-zinc-200">

                  <div
                    className="h-full rounded-full bg-zinc-400"
                    style={{
                      width: `${sentiment.neutral}%`,
                    }}
                  />

                </div>

              </div>


              {/* Negative */}

              <div className="mt-3">

                <div className="flex justify-between text-xs">

                  <span className="text-zinc-500">
                    Negative
                  </span>

                  <span className="font-medium text-zinc-700">
                    {sentiment.negative}%
                  </span>

                </div>

                <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-zinc-200">

                  <div
                    className="h-full rounded-full bg-red-400"
                    style={{
                      width: `${sentiment.negative}%`,
                    }}
                  />

                </div>

              </div>


              {/* Summary */}

              {sentiment.summary && (
                <p className="mt-4 text-xs leading-5 text-zinc-600">
                  {sentiment.summary}
                </p>
              )}

            </div>


            {/* =================================================
                Key Points
            ================================================= */}

            <div className="rounded-xl bg-zinc-50 p-4">

              <h3 className="text-xs font-semibold uppercase tracking-wide text-zinc-400">
                Key Discussion Points
              </h3>

              {sentiment.key_points?.length ? (

                <ul className="mt-3 space-y-2">

                  {sentiment.key_points.map(
                    (
                      point,
                      index,
                    ) => (
                      <li
                        key={index}
                        className="flex gap-2 text-xs leading-5 text-zinc-600"
                      >
                        <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-zinc-400" />

                        <span>
                          {point}
                        </span>

                      </li>
                    ),
                  )}

                </ul>

              ) : (

                <p className="mt-3 text-xs text-zinc-400">
                  No discussion insights yet.
                </p>

              )}

            </div>

          </div>


          {/* =================================================
              Discussion
          ================================================= */}

          <div className="mt-5">

            <div className="flex items-center justify-between">

              <h3 className="text-xs font-semibold uppercase tracking-wide text-zinc-400">
                Community Discussion
              </h3>

              <span className="text-xs text-zinc-400">
                {
                  feedback.discussion
                    ?.message_count ?? 0
                }{" "}
                messages
              </span>

            </div>


            {feedback.discussion
              ?.messages?.length ? (

              <div className="mt-3 space-y-2">

                {feedback.discussion.messages.map(
                  (message) => (
                    <div
                      key={
                        message.message_id
                      }
                      className="rounded-xl border border-zinc-100 bg-zinc-50 p-3"
                    >

                      <div className="flex items-center justify-between gap-3">

                        <span className="text-xs font-medium text-zinc-700">
                          {message.username}
                        </span>

                        <span className="text-[10px] text-zinc-400">
                          {new Date(
                            message.created_at,
                          ).toLocaleString()}
                        </span>

                      </div>

                      <p className="mt-1 text-xs leading-5 text-zinc-600">
                        {message.content}
                      </p>

                    </div>
                  ),
                )}

              </div>

            ) : (

              <div className="mt-3 rounded-xl border border-dashed border-zinc-200 p-8 text-center">

                <MessageSquare
                  size={18}
                  className="mx-auto text-zinc-300"
                />

                <p className="mt-2 text-xs text-zinc-400">
                  No discussion yet.
                </p>

                <p className="mt-1 text-[11px] text-zinc-300">
                  Community discussion will appear
                  here as people respond.
                </p>

              </div>

            )}

          </div>

        </div>
      )}

    </div>
  );
}


// ============================================================
// Page
// ============================================================

export default function FeedbackPage() {

  const [feedback, setFeedback] =
    useState<CommunityFeedback[]>([]);

  const [topFeedback, setTopFeedback] =
    useState<CommunityFeedback[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [search, setSearch] =
    useState("");

  const [sort, setSort] =
    useState("relevance");

  const [status, setStatus] =
    useState("");


  // ==========================================================
  // Load
  // ==========================================================

  useEffect(() => {

    async function loadFeedback() {

      try {

        setLoading(true);

        const [
          feedbackData,
          topData,
        ] = await Promise.all([
          getFeedback({
            limit: 50,
            sort,
            status:
              status || undefined,
          }),

          getTopFeedback({
            limit: 10,
            status: "open",
          }),
        ]);

        setFeedback(
          feedbackData,
        );

        setTopFeedback(
          topData,
        );

        setError(null);

      } catch (error) {

        setError(
          error instanceof Error
            ? error.message
            : "Failed to load feedback.",
        );

      } finally {

        setLoading(false);

      }

    }

    loadFeedback();

  }, [sort, status]);


  // ==========================================================
  // Search
  // ==========================================================

  const filteredFeedback =
    useMemo(() => {

      const query =
        search
          .trim()
          .toLowerCase();

      if (!query) {
        return feedback;
      }

      return feedback.filter(
        (item) =>
          item.suggestion
            .toLowerCase()
            .includes(query) ||

          item.author_name
            .toLowerCase()
            .includes(query) ||

          item.source
            ?.toLowerCase()
            .includes(query) ||

          item.status
            .toLowerCase()
            .includes(query),
      );

    }, [
      feedback,
      search,
    ]);


  // ==========================================================
  // Stats
  // ==========================================================

  const totalVotes =
    feedback.reduce(
      (
        total,
        item,
      ) =>
        total +
        item.upvotes +
        item.downvotes,
      0,
    );


  const totalDiscussion =
    feedback.reduce(
      (
        total,
        item,
      ) =>
        total +
        (
          item.discussion
            ?.message_count ?? 0
        ),
      0,
    );


  const positiveFeedback =
    feedback.filter(
      (item) =>
        item.discussion
          ?.sentiment
          ?.overall === "positive",
    ).length;


  // ==========================================================
  // Render
  // ==========================================================

  return (
    <main className="min-h-screen bg-zinc-50 px-6 py-8">

      <div className="mx-auto max-w-7xl">

        {/* ====================================================
            Header
        ==================================================== */}

        <div>

          <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-zinc-400">

            <TrendingUp size={14} />

            Community Intelligence

          </div>

          <h1 className="mt-2 text-2xl font-semibold tracking-tight text-zinc-950">
            Feedback
          </h1>

          <p className="mt-1 text-sm text-zinc-500">
            Understand what your community
            wants, discusses, and supports.
          </p>

        </div>


        {/* ====================================================
            Stats
        ==================================================== */}

        <div className="mt-7 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

          <StatCard
            label="Suggestions"
            value={feedback.length}
          />

          <StatCard
            label="Total Votes"
            value={totalVotes}
          />

          <StatCard
            label="Discussions"
            value={totalDiscussion}
          />

          <StatCard
            label="Positive Signals"
            value={positiveFeedback}
          />

        </div>


        {/* ====================================================
            Top Feedback
        ==================================================== */}

        {topFeedback.length > 0 && (

          <section className="mt-8">

            <div className="mb-4 flex items-center gap-2">

              <TrendingUp
                size={17}
                className="text-zinc-500"
              />

              <h2 className="text-sm font-semibold text-zinc-950">
                Top Supported Suggestions
              </h2>

            </div>


            <div className="grid gap-3 lg:grid-cols-3">

              {topFeedback.map(
                (
                  item,
                  index,
                ) => (

                  <div
                    key={item._id}
                    className="rounded-2xl border border-zinc-200 bg-white p-5"
                  >

                    <div className="flex items-center justify-between">

                      <span className="text-lg font-semibold text-zinc-300">
                        #{index + 1}
                      </span>

                      <div className="flex items-center gap-1.5 text-xs font-medium text-zinc-600">

                        <ThumbsUp
                          size={13}
                        />

                        {item.upvotes}

                      </div>

                    </div>


                    <p className="mt-3 text-sm font-medium leading-6 text-zinc-800">
                      {item.suggestion}
                    </p>


                    <div className="mt-4 flex items-center justify-between">

                      <span className="text-[11px] text-zinc-400">
                        {item.author_name}
                      </span>

                      <span className="flex items-center gap-1.5 text-[11px] text-zinc-400">

                        <MessageSquare
                          size={12}
                        />

                        {
                          item.discussion
                            ?.message_count ?? 0
                        }

                      </span>

                    </div>

                  </div>

                ),
              )}

            </div>

          </section>

        )}


        {/* ====================================================
            Filters
        ==================================================== */}

        <section className="mt-8">

          <div className="flex flex-col gap-3 sm:flex-row">

            <div className="relative flex-1">

              <Search
                size={16}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400"
              />

              <input
                value={search}
                onChange={(event) =>
                  setSearch(
                    event.target.value,
                  )
                }
                placeholder="Search suggestions, users..."
                className="h-10 w-full rounded-xl border border-zinc-200 bg-white pl-9 pr-4 text-sm text-zinc-900 outline-none placeholder:text-zinc-400 focus:border-zinc-400"
              />

            </div>


            <select
              value={sort}
              onChange={(event) =>
                setSort(
                  event.target.value,
                )
              }
              className="h-10 rounded-xl border border-zinc-200 bg-white px-3 text-sm text-zinc-600 outline-none"
            >

              <option value="relevance">
                Most relevant
              </option>

              <option value="most_discussed">
                Most discussed
              </option>

              <option value="newest">
                Newest
              </option>

              <option value="oldest">
                Oldest
              </option>

            </select>


            <select
              value={status}
              onChange={(event) =>
                setStatus(
                  event.target.value,
                )
              }
              className="h-10 rounded-xl border border-zinc-200 bg-white px-3 text-sm text-zinc-600 outline-none"
            >

              <option value="">
                All status
              </option>

              <option value="open">
                Open
              </option>

              <option value="new">
                New
              </option>

              <option value="reviewed">
                Reviewed
              </option>

              <option value="actionable">
                Actionable
              </option>

            </select>

          </div>

        </section>


        {/* ====================================================
            Feedback List
        ==================================================== */}

        <section className="mt-5">

          {loading ? (

            <div className="rounded-2xl border border-zinc-200 bg-white p-12 text-center text-sm text-zinc-400">
              Loading feedback...
            </div>

          ) : error ? (

            <div className="rounded-2xl border border-red-100 bg-red-50 p-6 text-sm text-red-600">
              {error}
            </div>

          ) : filteredFeedback.length ===
            0 ? (

            <div className="rounded-2xl border border-zinc-200 bg-white p-12 text-center">

              <MessageSquare
                size={20}
                className="mx-auto text-zinc-300"
              />

              <p className="mt-3 text-sm font-medium text-zinc-700">
                No feedback found
              </p>

              <p className="mt-1 text-xs text-zinc-400">
                Try changing your search
                or filters.
              </p>

            </div>

          ) : (

            <div className="space-y-3">

              {filteredFeedback.map(
                (item) => (
                  <FeedbackCard
                    key={item._id}
                    feedback={item}
                  />
                ),
              )}

            </div>

          )}

        </section>

      </div>

    </main>
  );
}


// ============================================================
// Stat Card
// ============================================================

function StatCard({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-5">

      <p className="text-xs font-medium uppercase tracking-wide text-zinc-400">
        {label}
      </p>

      <p className="mt-2 text-2xl font-semibold tracking-tight text-zinc-950">
        {value}
      </p>

    </div>
  );
}