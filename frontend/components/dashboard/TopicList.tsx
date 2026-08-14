import {
  Hash,
  TrendingUp,
} from "lucide-react";

import type { CommunityTrend } from "@/types/api";

interface TopicListProps {
  topics: CommunityTrend[];
}

export default function TopicList({
  topics,
}: TopicListProps) {
  return (
    <div className="rounded-2xl border border-zinc-200 bg-white">
      <div className="flex items-center justify-between border-b border-zinc-100 px-5 py-4">
        <div>
          <h2 className="text-sm font-semibold text-zinc-950">
            Trending topics
          </h2>

          <p className="mt-0.5 text-xs text-zinc-400">
            Most discussed community topics
          </p>
        </div>

        <TrendingUp
          size={17}
          className="text-zinc-400"
        />
      </div>

      <div className="divide-y divide-zinc-100">
        {topics.length === 0 ? (
          <div className="px-5 py-8 text-center text-sm text-zinc-400">
            No topic data available.
          </div>
        ) : (
          topics.map((topic, index) => (
            <div
              key={`${topic.topic}-${index}`}
              className="flex items-center justify-between px-5 py-3.5"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-zinc-100">
                  <Hash
                    size={14}
                    className="text-zinc-500"
                  />
                </div>

                <span className="text-sm text-zinc-700">
                  {topic.topic || "Unknown"}
                </span>
              </div>

              <span className="text-xs font-medium text-zinc-400">
                {topic.mentions} mentions
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}