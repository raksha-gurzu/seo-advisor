import type { ReactNode } from "react";

import { cn } from "@/shared/lib/utils";

/** One number with its label. Numbers use tabular figures so columns line up. */
export function Stat({
  label,
  value,
  hint,
  tone = "default",
  icon,
}: {
  label: string;
  value: ReactNode;
  hint?: ReactNode;
  tone?: "default" | "success" | "critical" | "warning";
  icon?: ReactNode;
}) {
  return (
    <div className="rounded-xl border bg-card px-4 py-3.5 shadow-xs">
      <div className="flex items-center justify-between text-xs font-medium text-muted-foreground [&_svg]:size-3.5">
        {label}
        {icon}
      </div>
      <div
        className={cn(
          "mt-1.5 text-2xl font-semibold tracking-tight tabular-nums",
          tone === "success" && "text-success",
          tone === "critical" && "text-critical",
          tone === "warning" && "text-warning",
        )}
      >
        {value}
      </div>
      {hint && <div className="mt-0.5 truncate text-xs text-muted-foreground">{hint}</div>}
    </div>
  );
}
