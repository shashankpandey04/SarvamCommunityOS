"use client";

import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api";

type Contributor = {
  discord_id: string;
  username: string;
  impact_score: number;
  message_count: number;
  channels: string[];
  first_seen: string;
  last_active: string;
};

export default function ContributorsPage() {
  const [contributors, setContributors] = useState<
    Contributor[]
  >([]);

  const [selected, setSelected] =
    useState<Contributor | null>(null);

  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] =
    useState(false);

  const [error, setError] = useState<string | null>(
    null
  );

  async function loadContributors() {
    try {
      setLoading(true);
      setError(null);

      const result = await apiFetch<Contributor[]>(
        "/api/contributors/leaderboard?limit=10"
      );

      setContributors(result);
    } catch (error) {
      console.error(
        "Failed to load contributors:",
        error
      );

      setError(
        "Unable to load contributors."
      );
    } finally {
      setLoading(false);
    }
  }

  async function loadContributor(
    discordId: string
  ) {
    try {
      setDetailLoading(true);

      const contributor =
        await apiFetch<Contributor>(
          `/api/contributors/${discordId}`
        );

      setSelected(contributor);
    } catch (error) {
      console.error(
        "Failed to load contributor:",
        error
      );
    } finally {
      setDetailLoading(false);
    }
  }

  useEffect(() => {
    loadContributors();
  }, []);

  if (loading) {
    return <ContributorsSkeleton />;
  }

  return (
    <div className="space-y-8">

      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">

        <div>

          <p className="text-xs font-medium uppercase tracking-wider text-zinc-400">
            Community
          </p>

          <h1 className="mt-2 text-2xl font-semibold tracking-tight text-zinc-950">
            Contributors
          </h1>

          <p className="mt-1 text-sm text-zinc-500">
            Recognize the people actively contributing
            to the community.
          </p>

        </div>

        <button
          onClick={loadContributors}
          className="rounded-lg border border-zinc-200 bg-white px-4 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-50"
        >
          Refresh
        </button>

      </div>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-5">

          <p className="text-sm text-red-700">
            {error}
          </p>

        </div>
      )}

      <section className="rounded-xl border border-zinc-200 bg-white">

        <div className="border-b border-zinc-200 px-6 py-5">

          <h2 className="text-sm font-semibold text-zinc-950">
            Impact Leaderboard
          </h2>

          <p className="mt-1 text-xs text-zinc-500">
            Top contributors ranked by impact score.
          </p>

        </div>


        {contributors.length === 0 ? (
          <div className="px-6 py-12 text-center">

            <p className="text-sm text-zinc-500">
              No contributors found.
            </p>

          </div>
        ) : (
          <div className="divide-y divide-zinc-100">

            {contributors.map(
              (contributor, index) => (
                <ContributorRow
                  key={contributor.discord_id}
                  contributor={contributor}
                  rank={index + 1}
                  onClick={() =>
                    loadContributor(
                      contributor.discord_id
                    )
                  }
                />
              )
            )}

          </div>
        )}

      </section>

      {(selected || detailLoading) && (
        <ContributorDetail
          contributor={selected}
          loading={detailLoading}
          onClose={() => setSelected(null)}
        />
      )}

    </div>
  );
}

function ContributorRow({
  contributor,
  rank,
  onClick,
}: {
  contributor: Contributor;
  rank: number;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="flex w-full items-center gap-4 px-6 py-5 text-left transition hover:bg-zinc-50"
    >

      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-zinc-100 text-sm font-semibold text-zinc-600">
        {rank}
      </div>

      <div className="min-w-0 flex-1">

        <p className="truncate text-sm font-semibold text-zinc-900">
          {contributor.username}
        </p>

        <p className="mt-1 truncate text-xs text-zinc-400">
          {contributor.discord_id}
        </p>

      </div>

      <div className="hidden text-right sm:block">

        <p className="text-xs text-zinc-400">
          Messages
        </p>

        <p className="mt-1 text-sm font-medium text-zinc-800">
          {contributor.message_count}
        </p>

      </div>

      <div className="hidden text-right md:block">

        <p className="text-xs text-zinc-400">
          Channels
        </p>

        <p className="mt-1 text-sm font-medium text-zinc-800">
          {contributor.channels.length}
        </p>

      </div>

      <div className="w-20 text-right">

        <p className="text-xs text-zinc-400">
          Impact
        </p>

        <p className="mt-1 text-lg font-semibold text-zinc-950">
          {contributor.impact_score}
        </p>

      </div>

    </button>
  );
}

function ContributorDetail({
  contributor,
  loading,
  onClose,
}: {
  contributor: Contributor | null;
  loading: boolean;
  onClose: () => void;
}) {
  return (
    <section className="rounded-xl border border-zinc-200 bg-white">

      <div className="flex items-center justify-between border-b border-zinc-200 px-6 py-5">

        <div>

          <h2 className="text-sm font-semibold text-zinc-950">
            Contributor Details
          </h2>

          <p className="mt-1 text-xs text-zinc-500">
            Individual community contribution profile.
          </p>

        </div>

        <button
          onClick={onClose}
          className="text-xs font-medium text-zinc-400 hover:text-zinc-700"
        >
          Close
        </button>

      </div>


      {loading ? (
        <div className="grid gap-4 p-6 sm:grid-cols-2 lg:grid-cols-4">

          {[1, 2, 3, 4].map((item) => (
            <div
              key={item}
              className="h-24 animate-pulse rounded-lg bg-zinc-100"
            />
          ))}

        </div>
      ) : contributor ? (
        <div className="p-6 space-y-6">

          <div>

            <h3 className="text-lg font-semibold text-zinc-950">
              {contributor.username}
            </h3>

            <p className="mt-1 font-mono text-xs text-zinc-400">
              {contributor.discord_id}
            </p>

          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

            <DetailCard
              label="Impact Score"
              value={contributor.impact_score}
            />

            <DetailCard
              label="Messages"
              value={contributor.message_count}
            />

            <DetailCard
              label="Channels"
              value={contributor.channels.length}
            />

            <DetailCard
              label="Active"
              value={formatDate(
                contributor.last_active
              )}
            />

          </div>

          <div>

            <p className="text-xs font-medium uppercase tracking-wide text-zinc-400">
              Channels
            </p>

            <div className="mt-3 flex flex-wrap gap-2">

              {contributor.channels.map(
                (channel) => (
                  <span
                    key={channel}
                    className="rounded-md bg-zinc-100 px-2.5 py-1 text-xs font-medium text-zinc-600"
                  >
                    #{channel}
                  </span>
                )
              )}

            </div>

          </div>

          <div className="grid gap-4 border-t border-zinc-100 pt-5 sm:grid-cols-2">

            <InfoItem
              label="First seen"
              value={formatDate(
                contributor.first_seen
              )}
            />

            <InfoItem
              label="Last active"
              value={formatDate(
                contributor.last_active
              )}
            />

          </div>

        </div>
      ) : null}

    </section>
  );
}

function DetailCard({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="rounded-lg border border-zinc-200 p-4">

      <p className="text-xs text-zinc-400">
        {label}
      </p>

      <p className="mt-2 text-lg font-semibold text-zinc-950">
        {value}
      </p>

    </div>
  );
}

function InfoItem({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div>

      <p className="text-xs text-zinc-400">
        {label}
      </p>

      <p className="mt-1 text-sm font-medium text-zinc-700">
        {value}
      </p>

    </div>
  );
}

function formatDate(
  value: string
) {
  return new Date(value).toLocaleString(
    undefined,
    {
      dateStyle: "medium",
      timeStyle: "short",
    }
  );
}

function ContributorsSkeleton() {
  return (
    <div className="space-y-8">

      <div className="space-y-2">

        <div className="h-7 w-48 animate-pulse rounded bg-zinc-200" />

        <div className="h-4 w-80 animate-pulse rounded bg-zinc-200" />

      </div>


      <div className="overflow-hidden rounded-xl border border-zinc-200 bg-white">

        {[1, 2, 3, 4, 5].map(
          (item) => (
            <div
              key={item}
              className="h-20 animate-pulse border-b border-zinc-100 bg-white"
            />
          )
        )}

      </div>

    </div>
  );
}