import { CircleCheck, CircleDashed } from "lucide-react";

import { cn } from "@/shared/lib/utils";

/** The six stages of the product and which ones work today (PLAN.md). */
const STAGES = [
  { name: "Know the site", detail: "robots.txt, sitemaps, types", ready: true },
  { name: "Find problems", detail: "crawl, rules, evidence", ready: false },
  { name: "See what matters", detail: "Search Console, ranking", ready: false },
  { name: "Write the fix", detail: "drafts that people review", ready: false },
  { name: "Apply", detail: "browser extension", ready: false },
  { name: "Measure", detail: "clicks after 4, 8, 12 weeks", ready: false },
] as const;

export function StageStrip() {
  return (
    <ol
      className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6"
      aria-label="Product stages"
    >
      {STAGES.map((stage, index) => (
        <li
          key={stage.name}
          className={cn(
            "relative rounded-lg border px-3 py-2.5",
            stage.ready ? "border-primary/30 bg-accent/60" : "bg-card/60",
          )}
        >
          <div className="flex items-center gap-1.5 text-xs font-medium">
            {stage.ready ? (
              <CircleCheck className="size-3.5 text-primary" aria-label="Works now" />
            ) : (
              <CircleDashed className="size-3.5 text-muted-foreground" aria-label="Planned" />
            )}
            <span className="text-muted-foreground tabular-nums">{index + 1}</span>
            <span className={stage.ready ? "text-accent-foreground" : ""}>{stage.name}</span>
          </div>
          <p className="mt-0.5 truncate text-[11px] text-muted-foreground">{stage.detail}</p>
        </li>
      ))}
    </ol>
  );
}
