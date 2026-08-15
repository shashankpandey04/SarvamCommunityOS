"use client";

import { usePathname } from "next/navigation";
import {
  Activity,
  CalendarDays,
} from "lucide-react";


const pageTitles: Record<string, string> = {
  "/dashboard": "Overview",
  "/analytics": "Analytics",
  "/contributors": "Contributors",
  "/knowledge": "Knowledge",
  "/documents": "Documents",
  "/feedback": "Feedback",
  "/escalations": "Escalations",
};


function getPageTitle(
  pathname: string,
) {
  if (pageTitles[pathname]) {
    return pageTitles[pathname];
  }

  const matchedRoute = Object.keys(
    pageTitles,
  ).find(
    (route) =>
      route !== "/dashboard" &&
      pathname.startsWith(
        `${route}/`,
      ),
  );

  return matchedRoute
    ? pageTitles[matchedRoute]
    : "Community Intelligence";
}


export default function Header() {

  const pathname =
    usePathname();

  const title =
    getPageTitle(pathname);


  const today =
    new Intl.DateTimeFormat(
      "en-IN",
      {
        weekday: "short",
        day: "numeric",
        month: "short",
        year: "numeric",
      },
    ).format(new Date());


  return (
    <header className="sticky top-0 z-30 flex h-20 items-center justify-between border-b border-zinc-200 bg-white/95 px-8 backdrop-blur">

      {/* =====================================================
          Page Context
      ===================================================== */}

      <div>

        <div className="flex items-center gap-2">

          <p className="text-sm font-semibold tracking-tight text-zinc-950">
            {title}
          </p>

        </div>

        <p className="mt-0.5 text-xs text-zinc-500">
          Monitor, understand, and improve your community
        </p>

      </div>


      {/* =====================================================
          Right Side
      ===================================================== */}

      <div className="flex items-center gap-3">

        {/* Date */}

        <div className="hidden items-center gap-2 rounded-full border border-zinc-200 bg-white px-3 py-1.5 sm:flex">

          <CalendarDays
            size={13}
            className="text-zinc-400"
          />

          <span className="text-xs font-medium text-zinc-500">
            {today}
          </span>

        </div>


        {/* Status */}

        <div className="flex items-center gap-2 rounded-full border border-zinc-200 bg-zinc-50 px-3 py-1.5">

          <span className="relative flex h-2 w-2">

            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />

            <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />

          </span>

          <Activity
            size={13}
            className="text-zinc-400"
          />

          <span className="text-xs font-medium text-zinc-600">
            CommunityOS Online
          </span>

        </div>

      </div>

    </header>
  );
}