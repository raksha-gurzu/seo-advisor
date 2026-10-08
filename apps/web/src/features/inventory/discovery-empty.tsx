import { Radar } from "lucide-react";

import { RunDiscoveryButton } from "@/features/inventory/run-discovery-button";
import { EmptyState } from "@/shared/ui/empty-state";

const STEPS = [
  "Read robots.txt (RFC 9309).",
  "Read each sitemap that robots.txt names, else /sitemap.xml.",
  "Give each URL a page type from the site's rules.",
];

export function DiscoveryEmpty({ siteId, title }: { siteId: string; title: string }) {
  return (
    <EmptyState
      icon={<Radar />}
      title={title}
      action={<RunDiscoveryButton siteId={siteId} size="lg" />}
    >
      <ol className="mx-auto mt-3 space-y-1.5 text-left">
        {STEPS.map((step, index) => (
          <li key={step} className="flex gap-2.5">
            <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-accent text-[11px] font-semibold text-accent-foreground tabular-nums">
              {index + 1}
            </span>
            {step}
          </li>
        ))}
      </ol>
      <p className="mt-4 text-xs">
        Read-only. One request per second at most. Every request passes the SSRF guard.
      </p>
    </EmptyState>
  );
}
