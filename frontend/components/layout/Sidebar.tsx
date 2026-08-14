"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  BarChart3,
  Users,
  Brain,
  FileText,
  ShieldAlert,
  MessageSquare,
  CalendarDays,
  Settings,
} from "lucide-react";

const navigation = [
  {
    name: "Overview",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "Analytics",
    href: "/analytics",
    icon: BarChart3,
  },
  {
    name: "Contributors",
    href: "/contributors",
    icon: Users,
  },
  {
    name: "Knowledge",
    href: "/knowledge",
    icon: Brain,
  },
  {
    name: "Documents",
    href: "/documents",
    icon: FileText,
  }
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-64 flex-col border-r border-zinc-200 bg-white">
      {/* Brand */}

      <div className="flex h-20 items-center border-b border-zinc-200 px-6">
        <Link
          href="/dashboard"
          className="flex items-center gap-3"
        >
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-zinc-950 text-sm font-bold text-white">
            C
          </div>

          <div>
            <div className="text-[15px] font-semibold tracking-tight text-zinc-950">
              CommunityOS
            </div>

            <div className="text-xs text-zinc-500">
              Community Intelligence
            </div>
          </div>
        </Link>
      </div>

      {/* Navigation */}

      <nav className="flex-1 space-y-1 px-3 py-5">
        <div className="mb-3 px-3 text-[11px] font-medium uppercase tracking-wider text-zinc-400">
          Workspace
        </div>

        {navigation.map((item) => {
          const Icon = item.icon;

          const active =
            pathname === item.href ||
            pathname.startsWith(`${item.href}/`);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition ${
                active
                  ? "bg-zinc-100 font-medium text-zinc-950"
                  : "text-zinc-500 hover:bg-zinc-50 hover:text-zinc-900"
              }`}
            >
              <Icon
                size={17}
                strokeWidth={active ? 2.2 : 1.8}
              />

              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* Bottom */}

      <div className="border-t border-zinc-200 p-3">
        <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-zinc-500 transition hover:bg-zinc-50 hover:text-zinc-900">
          <Settings size={17} />
          Settings
        </button>
      </div>
    </aside>
  );
}