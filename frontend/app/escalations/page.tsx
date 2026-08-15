"use client";

import { useEffect, useMemo, useState } from "react";

import {
  AlertCircle,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Clock3,
  MessageSquare,
  Search,
  Send,
  ShieldAlert,
  User,
} from "lucide-react";

import {
  getEscalations,
  sendEscalationMessage,
  updateEscalationStatus,
} from "@/lib/api";


// ============================================================
// Types
// ============================================================

type EscalationMessage = {
  message_id?: string;
  user_id: string;
  username: string;
  content: string;
  source?: string;
  created_at?: string;
};

type Escalation = {
  _id: string;
  question: string;
  user_id: string;
  username: string;
  guild_id?: string;
  channel_id?: string;
  thread_id?: string;
  topic?: string;
  bot_answer?: string;
  status: string;
  messages?: EscalationMessage[];
  created_at?: string;
  updated_at?: string;
  closed_at?: string;
};


// ============================================================
// Helpers
// ============================================================

function statusLabel(status: string) {
  switch (status) {
    case "open":
      return "Open";

    case "in_progress":
      return "In Progress";

    case "resolved":
      return "Resolved";

    case "closed":
      return "Closed";

    default:
      return status;
  }
}


function statusClass(status: string) {
  switch (status) {
    case "open":
      return "bg-red-50 text-red-700";

    case "in_progress":
      return "bg-amber-50 text-amber-700";

    case "resolved":
      return "bg-emerald-50 text-emerald-700";

    case "closed":
      return "bg-zinc-100 text-zinc-500";

    default:
      return "bg-zinc-100 text-zinc-500";
  }
}


function formatDate(date?: string) {
  if (!date) return "Unknown";

  return new Date(date).toLocaleString();
}


// ============================================================
// Escalation Card
// ============================================================

function EscalationCard({
  escalation,
  onRefresh,
}: {
  escalation: Escalation;
  onRefresh: () => void;
}) {
  const [expanded, setExpanded] =
    useState(false);

  const [message, setMessage] =
    useState("");

  const [sending, setSending] =
    useState(false);

  const [updating, setUpdating] =
    useState(false);


  // ----------------------------------------------------------
  // Status
  // ----------------------------------------------------------

  async function changeStatus(
    status: string,
  ) {
    try {
      setUpdating(true);

      await updateEscalationStatus(
        escalation._id,
        status,
      );

      onRefresh();

    } catch (error) {
      console.error(error);

    } finally {
      setUpdating(false);
    }
  }


  // ----------------------------------------------------------
  // Send Discord Message
  // ----------------------------------------------------------

  async function sendMessage() {
    const content =
      message.trim();

    if (
      !content ||
      sending
    ) {
      return;
    }

    try {
      setSending(true);

      await sendEscalationMessage(
        escalation._id,
        {
          user_id: "dashboard",
          username: "CommunityOS Team",
          content,
        },
      );

      setMessage("");

      onRefresh();

    } catch (error) {
      console.error(error);

      alert(
        error instanceof Error
          ? error.message
          : "Failed to send message.",
      );

    } finally {
      setSending(false);
    }
  }


  return (
    <div className="overflow-hidden rounded-2xl border border-zinc-200 bg-white">

      {/* =====================================================
          Main Escalation
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

          {/* Priority */}

          <div className="flex w-16 shrink-0 flex-col items-center rounded-xl border border-zinc-200 px-2 py-3">

            <ShieldAlert
              size={16}
              className="text-zinc-400"
            />

            <span className="mt-1 text-[10px] uppercase tracking-wide text-zinc-400">
              Support
            </span>

          </div>


          {/* Content */}

          <div className="min-w-0 flex-1">

            {/* Metadata */}

            <div className="flex flex-wrap items-center gap-2">

              <span className="flex items-center gap-1 rounded-full bg-zinc-100 px-2.5 py-1 text-[10px] font-medium text-zinc-500">
                <User size={10} />
                {escalation.username}
              </span>

              {escalation.topic && (
                <span className="rounded-full bg-zinc-100 px-2.5 py-1 text-[10px] font-medium uppercase tracking-wide text-zinc-500">
                  {escalation.topic}
                </span>
              )}

              <span
                className={`rounded-full px-2.5 py-1 text-[10px] font-medium ${statusClass(
                  escalation.status,
                )}`}
              >
                {statusLabel(
                  escalation.status,
                )}
              </span>

            </div>


            {/* Question */}

            <p className="mt-3 text-sm font-semibold leading-6 text-zinc-900">
              {escalation.question}
            </p>


            {/* Bot answer */}

            {escalation.bot_answer && (
              <p className="mt-1 line-clamp-2 text-xs leading-5 text-zinc-400">
                {escalation.bot_answer}
              </p>
            )}


            {/* Metrics */}

            <div className="mt-4 flex flex-wrap items-center gap-4 text-xs text-zinc-400">

              <span className="flex items-center gap-1.5">
                <MessageSquare
                  size={13}
                />

                {escalation.messages
                  ?.length ?? 0}
              </span>

              <span className="flex items-center gap-1.5">
                <Clock3
                  size={13}
                />

                {formatDate(
                  escalation.created_at,
                )}
              </span>

            </div>

          </div>


          {/* Expand */}

          <div className="pt-1 text-zinc-400">

            {expanded ? (
              <ChevronUp
                size={18}
              />
            ) : (
              <ChevronDown
                size={18}
              />
            )}

          </div>

        </div>

      </button>


      {/* =====================================================
          Expanded Details
      ===================================================== */}

      {expanded && (
        <div className="border-t border-zinc-100 px-5 pb-5">

          {/* =================================================
              Details
          ================================================= */}

          <div className="grid gap-4 pt-5 lg:grid-cols-2">

            {/* User Question */}

            <div className="rounded-xl bg-zinc-50 p-4">

              <h3 className="text-xs font-semibold uppercase tracking-wide text-zinc-400">
                User Question
              </h3>

              <p className="mt-3 text-xs leading-5 text-zinc-600">
                {escalation.question}
              </p>

            </div>


            {/* Bot Answer */}

            <div className="rounded-xl bg-zinc-50 p-4">

              <h3 className="text-xs font-semibold uppercase tracking-wide text-zinc-400">
                CommunityOS Answer
              </h3>

              <p className="mt-3 text-xs leading-5 text-zinc-600">
                {escalation.bot_answer ||
                  "No bot answer available."}
              </p>

            </div>

          </div>


          {/* =================================================
              Status
          ================================================= */}

          <div className="mt-5 flex items-center justify-between">

            <h3 className="text-xs font-semibold uppercase tracking-wide text-zinc-400">
              Escalation Status
            </h3>

            <select
              value={
                escalation.status
              }
              disabled={updating}
              onChange={(event) =>
                changeStatus(
                  event.target.value,
                )
              }
              className="rounded-xl border border-zinc-200 bg-white px-3 py-2 text-xs text-zinc-600 outline-none"
            >

              <option value="open">
                Open
              </option>

              <option value="in_progress">
                In Progress
              </option>

              <option value="resolved">
                Resolved
              </option>

              <option value="closed">
                Closed
              </option>

            </select>

          </div>


          {/* =================================================
              Discord Conversation
          ================================================= */}

          <div className="mt-5">

            <div className="flex items-center justify-between">

              <h3 className="text-xs font-semibold uppercase tracking-wide text-zinc-400">
                Discord Conversation
              </h3>

              <span className="text-xs text-zinc-400">
                {escalation.messages
                  ?.length ?? 0}{" "}
                messages
              </span>

            </div>


            {escalation.messages?.length ? (

              <div className="mt-3 space-y-2">

                {escalation.messages.map(
                  (
                    item,
                    index,
                  ) => {

                    const dashboard =
                      item.source ===
                      "dashboard";

                    return (
                      <div
                        key={
                          item.message_id ||
                          index
                        }
                        className={`rounded-xl border p-3 ${
                          dashboard
                            ? "border-blue-100 bg-blue-50"
                            : "border-zinc-100 bg-zinc-50"
                        }`}
                      >

                        <div className="flex items-center justify-between gap-3">

                          <span className="text-xs font-medium text-zinc-700">
                            {item.username}
                          </span>

                          <div className="flex items-center gap-2">

                            {dashboard && (
                              <span className="text-[10px] text-blue-500">
                                Dashboard
                              </span>
                            )}

                            {item.created_at && (
                              <span className="text-[10px] text-zinc-400">
                                {formatDate(
                                  item.created_at,
                                )}
                              </span>
                            )}

                          </div>

                        </div>

                        <p className="mt-1 text-xs leading-5 text-zinc-600 whitespace-pre-wrap">
                          {item.content}
                        </p>

                      </div>
                    );

                  },
                )}

              </div>

            ) : (

              <div className="mt-3 rounded-xl border border-dashed border-zinc-200 p-8 text-center">

                <MessageSquare
                  size={18}
                  className="mx-auto text-zinc-300"
                />

                <p className="mt-2 text-xs text-zinc-400">
                  No conversation yet.
                </p>

              </div>

            )}

          </div>


          {/* =================================================
              Reply
          ================================================= */}

          <div className="mt-5">

            <h3 className="text-xs font-semibold uppercase tracking-wide text-zinc-400">
              Reply to Discord
            </h3>

            <div className="mt-3 flex gap-2">

              <textarea
                value={message}
                onChange={(event) =>
                  setMessage(
                    event.target.value,
                  )
                }
                onKeyDown={(event) => {

                  if (
                    event.key ===
                      "Enter" &&
                    !event.shiftKey
                  ) {
                    event.preventDefault();

                    sendMessage();
                  }

                }}
                rows={3}
                placeholder="Write a response..."
                className="min-h-[80px] flex-1 resize-none rounded-xl border border-zinc-200 bg-white px-3 py-2 text-xs text-zinc-700 outline-none placeholder:text-zinc-400 focus:border-zinc-400"
              />

              <button
                type="button"
                onClick={sendMessage}
                disabled={
                  sending ||
                  !message.trim()
                }
                className="self-end rounded-xl bg-zinc-950 px-4 py-2 text-xs font-medium text-white transition hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-40"
              >

                <span className="flex items-center gap-2">

                  <Send size={13} />

                  {sending
                    ? "Sending..."
                    : "Send"}

                </span>

              </button>

            </div>

            <p className="mt-2 text-[10px] text-zinc-400">
              This message will be sent directly
              to the Discord escalation thread.
            </p>

          </div>

        </div>
      )}

    </div>
  );
}


// ============================================================
// Page
// ============================================================

export default function EscalationsPage() {

  const [
    escalations,
    setEscalations,
  ] = useState<Escalation[]>([]);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState<string | null>(
    null,
  );

  const [
    search,
    setSearch,
  ] = useState("");

  const [
    status,
    setStatus,
  ] = useState("");


  // ==========================================================
  // Load
  // ==========================================================

  async function loadEscalations() {

    try {

      setLoading(true);

      const data =
        await getEscalations({
          status:
            status || undefined,
          limit: 100,
        });

      setEscalations(data);

      setError(null);

    } catch (error) {

      setError(
        error instanceof Error
          ? error.message
          : "Failed to load escalations.",
      );

    } finally {

      setLoading(false);

    }

  }


  useEffect(() => {
    loadEscalations();
  }, [status]);


  // ==========================================================
  // Search
  // ==========================================================

  const filteredEscalations =
    useMemo(() => {

      const query =
        search
          .trim()
          .toLowerCase();

      if (!query) {
        return escalations;
      }

      return escalations.filter(
        (item) =>
          item.question
            ?.toLowerCase()
            .includes(query) ||

          item.username
            ?.toLowerCase()
            .includes(query) ||

          item.topic
            ?.toLowerCase()
            .includes(query) ||

          item.status
            ?.toLowerCase()
            .includes(query),
      );

    }, [
      escalations,
      search,
    ]);


  // ==========================================================
  // Stats
  // ==========================================================

  const openCount =
    escalations.filter(
      (item) =>
        item.status ===
        "open",
    ).length;

  const inProgressCount =
    escalations.filter(
      (item) =>
        item.status ===
        "in_progress",
    ).length;

  const resolvedCount =
    escalations.filter(
      (item) =>
        item.status ===
        "resolved",
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

            <ShieldAlert
              size={14}
            />

            Support Operations

          </div>

          <h1 className="mt-2 text-2xl font-semibold tracking-tight text-zinc-950">
            Escalations
          </h1>

          <p className="mt-1 text-sm text-zinc-500">
            Review unresolved questions and
            respond directly to the community.
          </p>

        </div>


        {/* ====================================================
            Stats
        ==================================================== */}

        <div className="mt-7 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

          <StatCard
            label="Total Escalations"
            value={
              escalations.length
            }
            icon={
              <ShieldAlert
                size={15}
              />
            }
          />

          <StatCard
            label="Open"
            value={openCount}
            icon={
              <AlertCircle
                size={15}
              />
            }
          />

          <StatCard
            label="In Progress"
            value={
              inProgressCount
            }
            icon={
              <Clock3
                size={15}
              />
            }
          />

          <StatCard
            label="Resolved"
            value={
              resolvedCount
            }
            icon={
              <CheckCircle2
                size={15}
              />
            }
          />

        </div>


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
                placeholder="Search questions, users..."
                className="h-10 w-full rounded-xl border border-zinc-200 bg-white pl-9 pr-4 text-sm text-zinc-900 outline-none placeholder:text-zinc-400 focus:border-zinc-400"
              />

            </div>


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

              <option value="in_progress">
                In Progress
              </option>

              <option value="resolved">
                Resolved
              </option>

              <option value="closed">
                Closed
              </option>

            </select>

          </div>

        </section>


        {/* ====================================================
            Escalation List
        ==================================================== */}

        <section className="mt-5">

          {loading ? (

            <div className="rounded-2xl border border-zinc-200 bg-white p-12 text-center text-sm text-zinc-400">
              Loading escalations...
            </div>

          ) : error ? (

            <div className="rounded-2xl border border-red-100 bg-red-50 p-6 text-sm text-red-600">
              {error}
            </div>

          ) : filteredEscalations.length ===
            0 ? (

            <div className="rounded-2xl border border-zinc-200 bg-white p-12 text-center">

              <CheckCircle2
                size={20}
                className="mx-auto text-zinc-300"
              />

              <p className="mt-3 text-sm font-medium text-zinc-700">
                No escalations found
              </p>

              <p className="mt-1 text-xs text-zinc-400">
                Try changing your search or
                filters.
              </p>

            </div>

          ) : (

            <div className="space-y-3">

              {filteredEscalations.map(
                (item) => (

                  <EscalationCard
                    key={item._id}
                    escalation={item}
                    onRefresh={
                      loadEscalations
                    }
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
  icon,
}: {
  label: string;
  value: number;
  icon: React.ReactNode;
}) {

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-5">

      <div className="flex items-center gap-2 text-zinc-400">

        {icon}

        <p className="text-xs font-medium uppercase tracking-wide">
          {label}
        </p>

      </div>

      <p className="mt-2 text-2xl font-semibold tracking-tight text-zinc-950">
        {value}
      </p>

    </div>
  );
}