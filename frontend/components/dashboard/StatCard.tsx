interface StatCardProps {
  label: string;
  value: string | number;
  description?: string;
  icon: React.ReactNode;
}

export default function StatCard({
  label,
  value,
  description,
  icon,
}: StatCardProps) {
  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-5">
      <div className="mb-5 flex items-start justify-between">
        <div className="text-sm text-zinc-500">
          {label}
        </div>

        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-zinc-100 text-zinc-600">
          {icon}
        </div>
      </div>

      <div className="text-3xl font-semibold tracking-tight text-zinc-950">
        {value}
      </div>

      {description && (
        <div className="mt-1 text-xs text-zinc-400">
          {description}
        </div>
      )}
    </div>
  );
}