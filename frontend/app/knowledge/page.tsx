"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

type Candidate = {
  _id: string;
  question: string;
  answer: string;
  topic: string;
  category: string;
  keywords: string[];
  source?: string;
  status: string;
  occurrences?: number;
  question_variants?: string[];
  created_at?: string;
  updated_at?: string;
};

type Knowledge = {
  _id: string;
  title: string;
  content: string;
  topic: string;
  category: string;
  tags: string[];
  source?: string;
  source_type?: string;
  generated_by?: string;
  occurrences?: number;
  question_variants?: string[];
  created_at?: string;
  updated_at?: string;
};

type KnowledgeResponse = {
  page: number;
  limit: number;
  total: number;
  total_pages: number;
  knowledge: Knowledge[];
};

export default function KnowledgePage() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [knowledge, setKnowledge] = useState<Knowledge[]>([]);

  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalKnowledge, setTotalKnowledge] = useState(0);

  const [search, setSearch] = useState("");
  const [searchInput, setSearchInput] = useState("");

  const [loadingCandidates, setLoadingCandidates] =
    useState(true);

  const [loadingKnowledge, setLoadingKnowledge] =
    useState(true);

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const [editingCandidate, setEditingCandidate] =
    useState<Candidate | null>(null);

  const [editingKnowledge, setEditingKnowledge] =
    useState<Knowledge | null>(null);

  const [selectedKnowledge, setSelectedKnowledge] =
    useState<string[]>([]);

  const [showMergeModal, setShowMergeModal] =
    useState(false);

  const [mergePrimaryId, setMergePrimaryId] =
    useState<string>("");

  // =========================================================
  // Load Candidates
  // =========================================================

  async function loadCandidates() {
    try {
      setLoadingCandidates(true);

      const data = await apiFetch<Candidate[]>(
        "/api/knowledge/candidates",
      );

      setCandidates(data);
    } catch (err) {
      console.error(err);
      setError(
        "Failed to load knowledge candidates.",
      );
    } finally {
      setLoadingCandidates(false);
    }
  }

  // =========================================================
  // Load Knowledge
  // =========================================================

  async function loadKnowledge(
    requestedPage = page,
    requestedSearch = search,
  ) {
    try {
      setLoadingKnowledge(true);

      const params = new URLSearchParams({
        page: String(requestedPage),
        limit: "10",
      });

      if (requestedSearch.trim()) {
        params.set(
          "search",
          requestedSearch.trim(),
        );
      }

      const data =
        await apiFetch<KnowledgeResponse>(
          `/api/knowledge/?${params.toString()}`,
        );

      setKnowledge(data.knowledge);
      setTotalPages(data.total_pages);
      setTotalKnowledge(data.total);
    } catch (err) {
      console.error(err);
      setError(
        "Failed to load knowledge.",
      );
    } finally {
      setLoadingKnowledge(false);
    }
  }

  // =========================================================
  // Initial Load
  // =========================================================

  useEffect(() => {
    loadCandidates();
  }, []);

  useEffect(() => {
    loadKnowledge(page, search);
  }, [page, search]);

  // =========================================================
  // Search
  // =========================================================

  function handleSearch(
    event: React.FormEvent,
  ) {
    event.preventDefault();

    setPage(1);
    setSearch(searchInput.trim());
    setSelectedKnowledge([]);
  }

  function clearSearch() {
    setSearchInput("");
    setSearch("");
    setPage(1);
    setSelectedKnowledge([]);
  }

  // =========================================================
  // Candidate Approval
  // =========================================================

  async function approveCandidate(
    candidate: Candidate,
  ) {
    try {
      setSaving(true);

      await apiFetch(
        `/api/knowledge/candidates/${candidate._id}/approve`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            answer: candidate.answer,
          }),
        },
      );

      setEditingCandidate(null);

      await Promise.all([
        loadCandidates(),
        loadKnowledge(page, search),
      ]);
    } catch (err) {
      console.error(err);
      setError(
        "Failed to approve candidate.",
      );
    } finally {
      setSaving(false);
    }
  }

  // =========================================================
  // Candidate Rejection
  // =========================================================

  async function rejectCandidate(
    candidate: Candidate,
  ) {
    if (
      !window.confirm(
        "Reject this knowledge candidate?",
      )
    ) {
      return;
    }

    try {
      setSaving(true);

      await apiFetch(
        `/api/knowledge/candidates/${candidate._id}/reject`,
        {
          method: "POST",
        },
      );

      setEditingCandidate(null);

      await loadCandidates();
    } catch (err) {
      console.error(err);
      setError(
        "Failed to reject candidate.",
      );
    } finally {
      setSaving(false);
    }
  }

  // =========================================================
  // Update Knowledge
  // =========================================================

  async function updateKnowledge() {
    if (!editingKnowledge) {
      return;
    }

    try {
      setSaving(true);

      await apiFetch(
        `/api/knowledge/${editingKnowledge._id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            title: editingKnowledge.title,
            content: editingKnowledge.content,
            topic: editingKnowledge.topic,
            category: editingKnowledge.category,
            tags: editingKnowledge.tags,
          }),
        },
      );

      setEditingKnowledge(null);

      await loadKnowledge(page, search);
    } catch (err) {
      console.error(err);
      setError(
        "Failed to update knowledge.",
      );
    } finally {
      setSaving(false);
    }
  }

  // =========================================================
  // Selection
  // =========================================================

  function toggleKnowledge(
    knowledgeId: string,
  ) {
    setSelectedKnowledge((current) => {
      if (current.includes(knowledgeId)) {
        return current.filter(
          (id) => id !== knowledgeId,
        );
      }

      return [
        ...current,
        knowledgeId,
      ];
    });
  }

  function selectAllVisible() {
    const visibleIds = knowledge.map(
      (item) => item._id,
    );

    const allSelected = visibleIds.every(
      (id) =>
        selectedKnowledge.includes(id),
    );

    if (allSelected) {
      setSelectedKnowledge((current) =>
        current.filter(
          (id) =>
            !visibleIds.includes(id),
        ),
      );
    } else {
      setSelectedKnowledge((current) =>
        Array.from(
          new Set([
            ...current,
            ...visibleIds,
          ]),
        ),
      );
    }
  }

  // =========================================================
  // Open Merge
  // =========================================================

  function openMergeModal() {
    if (selectedKnowledge.length < 2) {
      return;
    }

    setMergePrimaryId(
      selectedKnowledge[0],
    );

    setShowMergeModal(true);
  }

  // =========================================================
  // Merge Knowledge
  // =========================================================

  async function mergeKnowledge() {
    if (
      selectedKnowledge.length < 2 ||
      !mergePrimaryId
    ) {
      return;
    }

    try {
      setSaving(true);

      await apiFetch(
        "/api/knowledge/merge",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            knowledge_ids:
              selectedKnowledge,
            primary_id:
              mergePrimaryId,
          }),
        },
      );

      setShowMergeModal(false);
      setSelectedKnowledge([]);
      setMergePrimaryId("");

      await loadKnowledge(
        page,
        search,
      );
    } catch (err) {
      console.error(err);
      setError(
        "Failed to merge knowledge.",
      );
    } finally {
      setSaving(false);
    }
  }

  // =========================================================
  // Helpers
  // =========================================================

  function formatDate(
    value?: string,
  ) {
    if (!value) {
      return "—";
    }

    return new Date(
      value,
    ).toLocaleString();
  }

  return (
    <main className="min-h-screen bg-zinc-50 text-zinc-950">
      <div className="mx-auto max-w-7xl px-6 py-8">

        {/* ================================================= */}
        {/* Header */}
        {/* ================================================= */}

        <div className="mb-8 flex items-start justify-between gap-6">

          <div>
            <p className="text-sm font-medium text-zinc-500">
              CommunityOS
            </p>

            <h1 className="mt-1 text-3xl font-semibold tracking-tight">
              Knowledge
            </h1>

            <p className="mt-2 max-w-2xl text-sm text-zinc-500">
              Review AI-generated knowledge and
              manage the trusted knowledge base.
            </p>
          </div>

          <button
            onClick={() => {
              loadCandidates();
              loadKnowledge(
                page,
                search,
              );
            }}
            className="rounded-lg border border-zinc-200 bg-white px-4 py-2 text-sm font-medium shadow-sm hover:bg-zinc-100"
          >
            Refresh
          </button>

        </div>

        {/* ================================================= */}
        {/* Error */}
        {/* ================================================= */}

        {error && (
          <div className="mb-6 flex items-center justify-between rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            <span>{error}</span>

            <button
              onClick={() =>
                setError("")
              }
              className="font-medium"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* ================================================= */}
        {/* Pending Review */}
        {/* ================================================= */}

        <section className="mb-10">

          <div className="mb-4 flex items-end justify-between">

            <div>
              <h2 className="text-lg font-semibold">
                Pending Review
              </h2>

              <p className="mt-1 text-sm text-zinc-500">
                AI-generated answers waiting for approval.
              </p>
            </div>

            <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-700">
              {candidates.length} pending
            </span>

          </div>

          {loadingCandidates ? (
            <div className="rounded-xl border border-zinc-200 bg-white p-8 text-center text-sm text-zinc-500">
              Loading candidates...
            </div>
          ) : candidates.length === 0 ? (
            <div className="rounded-xl border border-dashed border-zinc-300 bg-white p-10 text-center">
              <p className="font-medium">
                No pending candidates
              </p>

              <p className="mt-1 text-sm text-zinc-500">
                New AI-generated knowledge will appear here.
              </p>
            </div>
          ) : (
            <div className="space-y-4">

              {candidates.map(
                (candidate) => (
                  <div
                    key={candidate._id}
                    className="rounded-xl border border-zinc-200 bg-white p-5 shadow-sm"
                  >

                    <div className="flex items-start justify-between gap-6">

                      <div className="min-w-0 flex-1">

                        <div className="flex flex-wrap gap-2">

                          <span className="rounded-md bg-zinc-100 px-2 py-1 text-xs text-zinc-600">
                            {candidate.topic}
                          </span>

                          <span className="rounded-md bg-zinc-100 px-2 py-1 text-xs text-zinc-500">
                            {candidate.category}
                          </span>

                          {(candidate.occurrences ?? 1) >
                            1 && (
                            <span className="rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700">
                              Asked{" "}
                              {
                                candidate.occurrences
                              }{" "}
                              times
                            </span>
                          )}

                        </div>

                        <h3 className="mt-3 font-semibold">
                          {candidate.question}
                        </h3>

                        <p className="mt-2 line-clamp-3 whitespace-pre-wrap text-sm leading-6 text-zinc-600">
                          {candidate.answer}
                        </p>

                      </div>

                      <div className="flex shrink-0 gap-2">

                        <button
                          onClick={() =>
                            setEditingCandidate(
                              candidate,
                            )
                          }
                          className="rounded-lg border border-zinc-200 px-3 py-2 text-sm font-medium hover:bg-zinc-50"
                        >
                          Review
                        </button>

                        <button
                          disabled={saving}
                          onClick={() =>
                            approveCandidate(
                              candidate,
                            )
                          }
                          className="rounded-lg bg-zinc-950 px-3 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50"
                        >
                          Approve
                        </button>

                      </div>

                    </div>

                  </div>
                ),
              )}

            </div>
          )}

        </section>

        {/* ================================================= */}
        {/* Knowledge Base */}
        {/* ================================================= */}

        <section>

          <div className="mb-5">

            <div className="flex items-end justify-between">

              <div>
                <h2 className="text-lg font-semibold">
                  Knowledge Base
                </h2>

                <p className="mt-1 text-sm text-zinc-500">
                  Trusted knowledge available to CommunityOS.
                </p>
              </div>

              <span className="text-sm text-zinc-500">
                {totalKnowledge} entries
              </span>

            </div>

            {/* Search */}

            <form
              onSubmit={handleSearch}
              className="mt-5 flex gap-2"
            >

              <input
                value={searchInput}
                onChange={(event) =>
                  setSearchInput(
                    event.target.value,
                  )
                }
                placeholder="Search by keyword, topic, category..."
                className="min-w-0 flex-1 rounded-lg border border-zinc-200 bg-white px-4 py-2.5 text-sm outline-none focus:border-zinc-400"
              />

              <button
                type="submit"
                className="rounded-lg bg-zinc-950 px-5 py-2.5 text-sm font-medium text-white hover:bg-zinc-800"
              >
                Search
              </button>

              {search && (
                <button
                  type="button"
                  onClick={clearSearch}
                  className="rounded-lg border border-zinc-200 bg-white px-4 py-2.5 text-sm font-medium hover:bg-zinc-50"
                >
                  Clear
                </button>
              )}

            </form>

          </div>

          {/* ================================================= */}
          {/* Selection Toolbar */}
          {/* ================================================= */}

          {knowledge.length > 0 && (
            <div className="mb-4 flex items-center justify-between rounded-xl border border-zinc-200 bg-white px-4 py-3">

              <label className="flex cursor-pointer items-center gap-3 text-sm">

                <input
                  type="checkbox"
                  checked={
                    knowledge.length > 0 &&
                    knowledge.every(
                      (item) =>
                        selectedKnowledge.includes(
                          item._id,
                        ),
                    )
                  }
                  onChange={
                    selectAllVisible
                  }
                  className="h-4 w-4 rounded border-zinc-300"
                />

                Select all visible

              </label>

              {selectedKnowledge.length > 0 && (
                <div className="flex items-center gap-3">

                  <span className="text-sm text-zinc-500">
                    {
                      selectedKnowledge.length
                    }{" "}
                    selected
                  </span>

                  <button
                    disabled={
                      selectedKnowledge.length <
                      2
                    }
                    onClick={
                      openMergeModal
                    }
                    className="rounded-lg bg-zinc-950 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-40"
                  >
                    Merge Knowledge
                  </button>

                </div>
              )}

            </div>
          )}

          {/* ================================================= */}
          {/* Knowledge List */}
          {/* ================================================= */}

          {loadingKnowledge ? (
            <div className="rounded-xl border border-zinc-200 bg-white p-8 text-center text-sm text-zinc-500">
              Loading knowledge...
            </div>
          ) : knowledge.length === 0 ? (
            <div className="rounded-xl border border-dashed border-zinc-300 bg-white p-10 text-center">
              <p className="font-medium">
                No knowledge found
              </p>

              <p className="mt-1 text-sm text-zinc-500">
                {search
                  ? "Try a different search term."
                  : "Your knowledge base is empty."}
              </p>
            </div>
          ) : (
            <div className="space-y-3">

              {knowledge.map(
                (item) => {
                  const selected =
                    selectedKnowledge.includes(
                      item._id,
                    );

                  return (
                    <div
                      key={item._id}
                      className={`rounded-xl border bg-white p-5 shadow-sm transition ${
                        selected
                          ? "border-zinc-500 ring-1 ring-zinc-300"
                          : "border-zinc-200"
                      }`}
                    >

                      <div className="flex items-start gap-4">

                        {/* Checkbox */}

                        <input
                          type="checkbox"
                          checked={selected}
                          onChange={() =>
                            toggleKnowledge(
                              item._id,
                            )
                          }
                          className="mt-1 h-4 w-4 shrink-0 rounded border-zinc-300"
                        />

                        {/* Content */}

                        <div className="min-w-0 flex-1">

                          <div className="flex flex-wrap gap-2">

                            <span className="rounded-md bg-zinc-100 px-2 py-1 text-xs text-zinc-600">
                              {item.topic}
                            </span>

                            <span className="rounded-md bg-zinc-100 px-2 py-1 text-xs text-zinc-500">
                              {item.category}
                            </span>

                            {item.source && (
                              <span className="rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700">
                                {item.source}
                              </span>
                            )}

                            {(item.occurrences ?? 0) >
                              1 && (
                              <span className="rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700">
                                {
                                  item.occurrences
                                }{" "}
                                occurrences
                              </span>
                            )}

                          </div>

                          <h3 className="mt-3 font-semibold">
                            {item.title}
                          </h3>

                          <p className="mt-2 line-clamp-3 whitespace-pre-wrap text-sm leading-6 text-zinc-600">
                            {item.content}
                          </p>

                          {item.tags?.length >
                            0 && (
                            <div className="mt-3 flex flex-wrap gap-1.5">

                              {item.tags.map(
                                (tag) => (
                                  <span
                                    key={tag}
                                    className="rounded-md bg-zinc-100 px-2 py-1 text-xs text-zinc-500"
                                  >
                                    #{tag}
                                  </span>
                                ),
                              )}

                            </div>
                          )}

                        </div>

                        {/* Edit */}

                        <button
                          onClick={() =>
                            setEditingKnowledge({
                              ...item,
                              tags: [
                                ...(item.tags ??
                                  []),
                              ],
                            })
                          }
                          className="shrink-0 rounded-lg border border-zinc-200 px-3 py-2 text-sm font-medium hover:bg-zinc-50"
                        >
                          Edit
                        </button>

                      </div>

                      <div className="mt-4 ml-8 border-t border-zinc-100 pt-3 text-xs text-zinc-400">
                        Updated{" "}
                        {formatDate(
                          item.updated_at,
                        )}
                      </div>

                    </div>
                  );
                },
              )}

            </div>
          )}

          {/* ================================================= */}
          {/* Pagination */}
          {/* ================================================= */}

          {totalPages > 1 && (
            <div className="mt-6 flex items-center justify-between">

              <p className="text-sm text-zinc-500">
                Page {page} of{" "}
                {totalPages}
              </p>

              <div className="flex gap-2">

                <button
                  disabled={page <= 1}
                  onClick={() =>
                    setPage(
                      (current) =>
                        current - 1,
                    )
                  }
                  className="rounded-lg border border-zinc-200 bg-white px-4 py-2 text-sm font-medium disabled:opacity-40"
                >
                  Previous
                </button>

                <button
                  disabled={
                    page >= totalPages
                  }
                  onClick={() =>
                    setPage(
                      (current) =>
                        current + 1,
                    )
                  }
                  className="rounded-lg border border-zinc-200 bg-white px-4 py-2 text-sm font-medium disabled:opacity-40"
                >
                  Next
                </button>

              </div>

            </div>
          )}

        </section>

      </div>

      {/* ===================================================== */}
      {/* Candidate Review Modal */}
      {/* ===================================================== */}

      {editingCandidate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-6">

          <div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-2xl bg-white shadow-2xl">

            <div className="border-b border-zinc-200 px-6 py-5">

              <div className="flex justify-between">

                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-amber-600">
                    Pending Review
                  </p>

                  <h2 className="mt-1 text-xl font-semibold">
                    Review Knowledge Candidate
                  </h2>
                </div>

                <button
                  onClick={() =>
                    setEditingCandidate(
                      null,
                    )
                  }
                  className="text-xl text-zinc-400"
                >
                  ×
                </button>

              </div>

            </div>

            <div className="space-y-6 p-6">

              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-zinc-500">
                  Question
                </label>

                <div className="mt-2 rounded-lg bg-zinc-50 p-4 text-sm">
                  {editingCandidate.question}
                </div>
              </div>

              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-zinc-500">
                  Proposed Answer
                </label>

                <textarea
                  value={
                    editingCandidate.answer
                  }
                  onChange={(event) =>
                    setEditingCandidate({
                      ...editingCandidate,
                      answer:
                        event.target.value,
                    })
                  }
                  rows={12}
                  className="mt-2 w-full rounded-lg border border-zinc-200 px-4 py-3 text-sm leading-6 outline-none focus:border-zinc-400"
                />
              </div>

            </div>

            <div className="flex justify-between border-t border-zinc-200 bg-zinc-50 px-6 py-4">

              <button
                disabled={saving}
                onClick={() =>
                  rejectCandidate(
                    editingCandidate,
                  )
                }
                className="rounded-lg border border-red-200 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50"
              >
                Reject
              </button>

              <div className="flex gap-2">

                <button
                  onClick={() =>
                    setEditingCandidate(
                      null,
                    )
                  }
                  className="rounded-lg border border-zinc-200 bg-white px-4 py-2 text-sm font-medium"
                >
                  Cancel
                </button>

                <button
                  disabled={
                    saving ||
                    !editingCandidate.answer.trim()
                  }
                  onClick={() =>
                    approveCandidate(
                      editingCandidate,
                    )
                  }
                  className="rounded-lg bg-zinc-950 px-5 py-2 text-sm font-medium text-white disabled:opacity-50"
                >
                  {saving
                    ? "Approving..."
                    : "Approve Knowledge"}
                </button>

              </div>

            </div>

          </div>

        </div>
      )}

      {/* ===================================================== */}
      {/* Edit Existing Knowledge Modal */}
      {/* ===================================================== */}

      {editingKnowledge && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-6">

          <div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-2xl bg-white shadow-2xl">

            <div className="border-b border-zinc-200 px-6 py-5">

              <div className="flex justify-between">

                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-green-600">
                    Trusted Knowledge
                  </p>

                  <h2 className="mt-1 text-xl font-semibold">
                    Edit Knowledge
                  </h2>
                </div>

                <button
                  onClick={() =>
                    setEditingKnowledge(
                      null,
                    )
                  }
                  className="text-xl text-zinc-400"
                >
                  ×
                </button>

              </div>

            </div>

            <div className="space-y-5 p-6">

              <div>
                <label className="text-xs font-medium text-zinc-500">
                  Title
                </label>

                <input
                  value={
                    editingKnowledge.title
                  }
                  onChange={(event) =>
                    setEditingKnowledge({
                      ...editingKnowledge,
                      title:
                        event.target.value,
                    })
                  }
                  className="mt-2 w-full rounded-lg border border-zinc-200 px-4 py-2.5 text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">

                <div>
                  <label className="text-xs font-medium text-zinc-500">
                    Topic
                  </label>

                  <input
                    value={
                      editingKnowledge.topic
                    }
                    onChange={(event) =>
                      setEditingKnowledge({
                        ...editingKnowledge,
                        topic:
                          event.target.value,
                      })
                    }
                    className="mt-2 w-full rounded-lg border border-zinc-200 px-4 py-2.5 text-sm"
                  />
                </div>

                <div>
                  <label className="text-xs font-medium text-zinc-500">
                    Category
                  </label>

                  <input
                    value={
                      editingKnowledge.category
                    }
                    onChange={(event) =>
                      setEditingKnowledge({
                        ...editingKnowledge,
                        category:
                          event.target.value,
                      })
                    }
                    className="mt-2 w-full rounded-lg border border-zinc-200 px-4 py-2.5 text-sm"
                  />
                </div>

              </div>

              <div>
                <label className="text-xs font-medium text-zinc-500">
                  Answer / Content
                </label>

                <textarea
                  value={
                    editingKnowledge.content
                  }
                  onChange={(event) =>
                    setEditingKnowledge({
                      ...editingKnowledge,
                      content:
                        event.target.value,
                    })
                  }
                  rows={14}
                  className="mt-2 w-full rounded-lg border border-zinc-200 px-4 py-3 text-sm leading-6"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-zinc-500">
                  Tags
                </label>

                <input
                  value={
                    editingKnowledge.tags.join(
                      ", ",
                    )
                  }
                  onChange={(event) =>
                    setEditingKnowledge({
                      ...editingKnowledge,
                      tags: event.target.value
                        .split(",")
                        .map((tag) =>
                          tag.trim(),
                        )
                        .filter(Boolean),
                    })
                  }
                  className="mt-2 w-full rounded-lg border border-zinc-200 px-4 py-2.5 text-sm"
                />
              </div>

              {editingKnowledge
                .question_variants
                ?.length ? (
                <div>

                  <label className="text-xs font-medium text-zinc-500">
                    Question Variants
                  </label>

                  <div className="mt-2 space-y-2">

                    {editingKnowledge.question_variants.map(
                      (
                        question,
                        index,
                      ) => (
                        <div
                          key={index}
                          className="rounded-lg bg-zinc-50 px-3 py-2 text-sm text-zinc-600"
                        >
                          {question}
                        </div>
                      ),
                    )}

                  </div>

                </div>
              ) : null}

            </div>

            <div className="flex justify-end gap-2 border-t border-zinc-200 bg-zinc-50 px-6 py-4">

              <button
                onClick={() =>
                  setEditingKnowledge(
                    null,
                  )
                }
                className="rounded-lg border border-zinc-200 bg-white px-4 py-2 text-sm font-medium"
              >
                Cancel
              </button>

              <button
                disabled={
                  saving ||
                  !editingKnowledge.title.trim() ||
                  !editingKnowledge.content.trim()
                }
                onClick={
                  updateKnowledge
                }
                className="rounded-lg bg-zinc-950 px-5 py-2 text-sm font-medium text-white disabled:opacity-50"
              >
                {saving
                  ? "Saving..."
                  : "Save Changes"}
              </button>

            </div>

          </div>

        </div>
      )}

      {/* ===================================================== */}
      {/* Merge Knowledge Modal */}
      {/* ===================================================== */}

      {showMergeModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-6">

          <div className="w-full max-w-2xl rounded-2xl bg-white shadow-2xl">

            <div className="border-b border-zinc-200 px-6 py-5">

              <div className="flex justify-between">

                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-blue-600">
                    Knowledge Management
                  </p>

                  <h2 className="mt-1 text-xl font-semibold">
                    Merge Knowledge
                  </h2>
                </div>

                <button
                  onClick={() =>
                    setShowMergeModal(
                      false,
                    )
                  }
                  className="text-xl text-zinc-400"
                >
                  ×
                </button>

              </div>

              <p className="mt-2 text-sm text-zinc-500">
                These entries appear to represent
                the same knowledge. Choose which
                answer should remain as the canonical
                answer.
              </p>

            </div>

            <div className="max-h-[55vh] space-y-3 overflow-y-auto p-6">

              {selectedKnowledge.map(
                (id) => {
                  const item =
                    knowledge.find(
                      (entry) =>
                        entry._id === id,
                    );

                  if (!item) {
                    return null;
                  }

                  const primary =
                    mergePrimaryId ===
                    item._id;

                  return (
                    <button
                      key={item._id}
                      onClick={() =>
                        setMergePrimaryId(
                          item._id,
                        )
                      }
                      className={`w-full rounded-xl border p-4 text-left transition ${
                        primary
                          ? "border-zinc-950 bg-zinc-50 ring-1 ring-zinc-950"
                          : "border-zinc-200 hover:bg-zinc-50"
                      }`}
                    >

                      <div className="flex items-start justify-between gap-4">

                        <div className="min-w-0">

                          <div className="flex items-center gap-2">

                            <span
                              className={`h-2 w-2 rounded-full ${
                                primary
                                  ? "bg-zinc-950"
                                  : "bg-zinc-300"
                              }`}
                            />

                            <span className="text-xs font-medium uppercase tracking-wide text-zinc-400">
                              {primary
                                ? "Canonical Answer"
                                : "Merge Into Canonical"}
                            </span>

                          </div>

                          <p className="mt-2 font-medium">
                            {item.title}
                          </p>

                          <p className="mt-1 line-clamp-3 text-sm leading-5 text-zinc-500">
                            {item.content}
                          </p>

                        </div>

                        <span className="shrink-0 rounded-md bg-zinc-100 px-2 py-1 text-xs text-zinc-500">
                          {item.occurrences ??
                            1}{" "}
                          occurrences
                        </span>

                      </div>

                    </button>
                  );
                },
              )}

            </div>

            <div className="border-t border-zinc-200 bg-zinc-50 px-6 py-4">

              <div className="mb-4 rounded-lg bg-amber-50 px-3 py-2 text-xs leading-5 text-amber-700">
                The canonical answer will be kept.
                Question variants, tags, and occurrence
                counts from the other entries will be
                merged into it. The duplicate entries
                will then be removed.
              </div>

              <div className="flex justify-end gap-2">

                <button
                  disabled={saving}
                  onClick={() =>
                    setShowMergeModal(
                      false,
                    )
                  }
                  className="rounded-lg border border-zinc-200 bg-white px-4 py-2 text-sm font-medium"
                >
                  Cancel
                </button>

                <button
                  disabled={
                    saving ||
                    !mergePrimaryId
                  }
                  onClick={
                    mergeKnowledge
                  }
                  className="rounded-lg bg-zinc-950 px-5 py-2 text-sm font-medium text-white disabled:opacity-50"
                >
                  {saving
                    ? "Merging..."
                    : "Merge Knowledge"}
                </button>

              </div>

            </div>

          </div>

        </div>
      )}

    </main>
  );
}