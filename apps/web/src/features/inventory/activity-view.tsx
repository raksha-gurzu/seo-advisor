import { ChevronRight, FileCode2, ShieldCheck } from "lucide-react";
import { Fragment, useState } from "react";

import type { DiscoveryRun, FetchEvent } from "@/shared/lib/api";
import { formatBytes, formatCount, formatMs, pathOf } from "@/shared/lib/format";
import { cn } from "@/shared/lib/utils";
import { Badge, type BadgeTone } from "@/shared/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/ui/card";

const OUTCOME: Record<FetchEvent["outcome"], { label: string; tone: BadgeTone }> = {
  ok: { label: "Done", tone: "success" },
  redirect: { label: "Redirect", tone: "info" },
  too_large: { label: "Too large", tone: "warning" },
  cached: { label: "From cache", tone: "neutral" },
  disallowed: { label: "Not allowed", tone: "critical" },
  blocked: { label: "Blocked", tone: "critical" },
  error: { label: "Error", tone: "critical" },
};

function statusTone(event: FetchEvent): BadgeTone {
  const status = event.status;
  if (status === null || status === undefined) return OUTCOME[event.outcome].tone;
  if (status < 300) return "success";
  if (status < 400) return "info";
  if (event.kind === "robots" && status < 500 && status !== 429) return "neutral";
  return status < 500 ? "warning" : "critical";
}

/** What the owner needs to know about one request, in plain words. */
function explain(event: FetchEvent): string {
  if (event.kind === "robots") {
    if (event.outcome === "cached")
      return "robots.txt rules were read less than 24 hours ago; no request was sent.";
    if (event.outcome === "blocked") return `The SSRF guard stopped the request: ${event.detail}`;
    if (event.status === null || event.status === undefined)
      return "robots.txt could not be read, so everything is disallowed for now (RFC 9309).";
    if (event.status === 401 || event.status === 403)
      return "robots.txt is forbidden: we treat the site as fully disallowed.";
    if (event.status >= 500 || event.status === 429)
      return "The server failed: everything is disallowed until it answers (RFC 9309).";
    if (event.status >= 400) return "No robots.txt: RFC 9309 says that every URL is allowed.";
    return "robots.txt was read. Its rules apply to every later request.";
  }
  switch (event.outcome) {
    case "ok":
      return event.status === 200
        ? "The sitemap was downloaded within the size and time limits."
        : `The server answered HTTP ${event.status}.`;
    case "redirect":
      return "A redirect. The next hop passes every check again.";
    case "too_large":
      return "The body passed its size limit, so it was not used.";
    case "disallowed":
      return `robots.txt does not allow this URL, so it was not requested. ${event.detail}`;
    case "blocked":
      return `The SSRF guard stopped the request before it was sent: ${event.detail}`;
    case "error":
      return `The request failed: ${event.detail}.`;
    case "cached":
      return "Served from cache.";
  }
}

const GATES = [
  ["Scheme", "http or https only"],
  ["robots.txt", "read once per site, kept 24 hours"],
  ["Rate limit", "at least 1 s between requests to one host"],
  ["Port and address", "port 80 or 443; every DNS answer must be public"],
  ["Pinned connection", "connects only to the address that was checked"],
  ["Limits", "size limit, safe gzip, total time limit"],
  ["Redirects", "at most 5; each hop passes every check again"],
] as const;

export function ActivityView({ run }: { run: DiscoveryRun }) {
  const [open, setOpen] = useState<number | null>(null);
  const events = run.requests;
  const end = Math.max(1, ...events.map((e) => e.started_ms + e.waited_ms + e.duration_ms));
  const sent = events.filter((e) => e.status !== null && e.status !== undefined);
  const stopped = events.filter((e) => e.outcome === "blocked" || e.outcome === "disallowed");
  const bytes = events.reduce((sum, e) => sum + e.bytes, 0);

  return (
    <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_300px]">
      <Card className="overflow-hidden">
        <CardHeader>
          <div>
            <CardTitle>Requests of the last discovery</CardTitle>
            <CardDescription>
              {formatCount(sent.length)} sent · {formatBytes(bytes)} · {formatMs(run.duration_ms)}{" "}
              in total
              {stopped.length > 0 && ` · ${stopped.length} stopped before sending`}
            </CardDescription>
          </div>
          <div className="hidden items-center gap-3 text-[11px] text-muted-foreground sm:flex">
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-4 rounded-sm bg-[repeating-linear-gradient(135deg,var(--border)_0_3px,transparent_3px_6px)] ring-1 ring-border" />
              rate-limit wait
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-4 rounded-sm bg-primary" /> request
            </span>
          </div>
        </CardHeader>
        <ol className="border-t">
          {events.map((event, index) => {
            const left = (event.started_ms / end) * 100;
            const wait = (event.waited_ms / end) * 100;
            const work = Math.max(0.6, (event.duration_ms / end) * 100);
            const expanded = open === index;
            const Icon = event.kind === "robots" ? ShieldCheck : FileCode2;
            return (
              <li key={index} className="border-b last:border-0">
                <button
                  type="button"
                  aria-expanded={expanded}
                  onClick={() => setOpen(expanded ? null : index)}
                  className="grid w-full grid-cols-[20px_minmax(0,1fr)_auto] items-center gap-3 px-5 py-3 text-left transition-colors hover:bg-muted/50 md:grid-cols-[20px_minmax(0,1.3fr)_auto_minmax(0,1fr)_64px]"
                >
                  <ChevronRight
                    className={cn(
                      "size-4 text-muted-foreground transition-transform",
                      expanded && "rotate-90",
                    )}
                  />
                  <span className="flex min-w-0 items-center gap-2">
                    <Icon className="size-4 shrink-0 text-muted-foreground" />
                    <span className="truncate font-mono text-[13px]">{pathOf(event.url)}</span>
                  </span>
                  <span className="flex items-center gap-1.5">
                    <Badge tone={statusTone(event)} className="font-mono tabular-nums">
                      {event.status ?? "—"}
                    </Badge>
                    <Badge tone={OUTCOME[event.outcome].tone} className="hidden sm:inline-flex">
                      {OUTCOME[event.outcome].label}
                    </Badge>
                  </span>
                  <span className="relative hidden h-2 rounded-full bg-muted md:block" aria-hidden>
                    <span
                      className="absolute inset-y-0 rounded-l-sm bg-[repeating-linear-gradient(135deg,var(--border)_0_3px,transparent_3px_6px)]"
                      style={{ left: `${left}%`, width: `${wait}%` }}
                    />
                    <span
                      className="absolute inset-y-0 rounded-sm bg-primary"
                      style={{ left: `${left + wait}%`, width: `${work}%` }}
                    />
                  </span>
                  <span className="hidden text-right text-xs text-muted-foreground tabular-nums md:block">
                    {formatMs(event.duration_ms)}
                  </span>
                </button>
                {expanded && (
                  <div className="bg-muted/30 px-5 pt-1 pb-4 pl-12">
                    <p className="text-sm">{explain(event)}</p>
                    <dl className="mt-3 grid grid-cols-2 gap-x-6 gap-y-2 text-xs sm:grid-cols-4">
                      {(
                        [
                          [
                            "URL",
                            <span key="url" className="font-mono break-all">
                              {event.url}
                            </span>,
                          ],
                          ["Started", `+${formatMs(event.started_ms)}`],
                          ["Waited", formatMs(event.waited_ms)],
                          ["Took", formatMs(event.duration_ms)],
                          ["Size", formatBytes(event.bytes)],
                          ["Kind", event.kind === "robots" ? "robots.txt" : "page"],
                        ] as const
                      ).map(([label, value]) => (
                        <Fragment key={label}>
                          <div className={cn(label === "URL" && "col-span-2 sm:col-span-4")}>
                            <dt className="text-muted-foreground">{label}</dt>
                            <dd className="mt-0.5 tabular-nums">{value}</dd>
                          </div>
                        </Fragment>
                      ))}
                    </dl>
                  </div>
                )}
              </li>
            );
          })}
        </ol>
      </Card>

      <Card className="h-fit">
        <CardHeader>
          <div>
            <CardTitle>Checks on every request</CardTitle>
            <CardDescription>Each hop passes all seven. Any one can stop it.</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <ol className="space-y-2.5">
            {GATES.map(([name, detail], index) => (
              <li key={name} className="flex gap-3 text-sm">
                <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-accent text-[11px] font-semibold text-accent-foreground tabular-nums">
                  {index + 1}
                </span>
                <span>
                  <span className="font-medium">{name}</span>
                  <span className="block text-xs text-muted-foreground">{detail}</span>
                </span>
              </li>
            ))}
          </ol>
        </CardContent>
      </Card>
    </div>
  );
}
