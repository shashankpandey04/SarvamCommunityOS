"use client";

import { usePathname } from "next/navigation";

const pageTitles: Record<string, string> = {
  "/dashboard": "Overview",
  "/analytics": "Analytics",
  "/contributors": "Contributors",
  "/knowledge": "Knowledge",
  "/documents": "Documents",
  "/escalations": "Escalations",
  "/feedback": "Feedback",
};

export default function Header() {
  const pathname = usePathname();

  const title =
    pageTitles[pathname] ?? "Community Intelligence";

  return (
    <header className="sticky top-0 z-30 flex h-20 items-center justify-between border-b border-zinc-200 bg-white/95 px-8 backdrop-blur">

      <div>
        <p className="text-sm font-medium text-zinc-950">
          {title}
        </p>

        <p className="text-xs text-zinc-500">
          Monitor, understand, and improve your community
        </p>
      </div>

      <div className="flex items-center gap-2 rounded-full border border-zinc-200 bg-zinc-50 px-3 py-1.5">

        <span className="h-2 w-2 rounded-full bg-emerald-500" />

        <span className="text-xs font-medium text-zinc-600">
          CommunityOS Online
        </span>

      </div>

    </header>
  );
}