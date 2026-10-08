import { CircleCheck, TriangleAlert, OctagonX } from "lucide-react";

import type { InventoryProblem } from "@/shared/lib/api";
import { Badge } from "@/shared/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";

const PROBLEM_TEXT: Record<InventoryProblem["kind"], { label: string; serious: boolean }> = {
  sitemap_blocked: { label: "Sitemap blocked", serious: true },
  sitemap_unreadable: { label: "Sitemap unreadable", serious: true },
  sitemap_invalid: { label: "Sitemap not valid", serious: true },
  nested_sitemap_index: { label: "Index inside an index", serious: false },
  sitemap_on_other_host: { label: "Sitemap on another host (not read)", serious: false },
  url_on_other_host: { label: "URL on another host", serious: false },
  url_not_http: { label: "URL is not http or https", serious: false },
  duplicate_url: { label: "Duplicate URL", serious: false },
};

export function ProblemsList({ problems }: { problems: InventoryProblem[] }) {
  if (problems.length === 0) {
    return (
      <div className="flex items-center gap-2.5 rounded-xl border border-success/25 bg-success/5 px-4 py-3 text-sm">
        <CircleCheck className="size-4 shrink-0 text-success" />
        <span>
          <span className="font-medium">No problems.</span>{" "}
          <span className="text-muted-foreground">
            Every sitemap was read, and every URL is on the site's own host.
          </span>
        </span>
      </div>
    );
  }
  return (
    <Card>
      <CardHeader>
        <CardTitle>Problems</CardTitle>
        <Badge tone="warning">{problems.length}</Badge>
      </CardHeader>
      <CardContent className="space-y-2">
        {problems.map((problem, index) => {
          const text = PROBLEM_TEXT[problem.kind];
          const Icon = text.serious ? OctagonX : TriangleAlert;
          return (
            <div
              key={`${problem.kind}-${problem.url}-${index}`}
              className="flex gap-3 rounded-lg border px-3 py-2.5"
            >
              <Icon
                className={
                  text.serious ? "mt-0.5 size-4 text-critical" : "mt-0.5 size-4 text-warning"
                }
              />
              <div className="min-w-0 text-sm">
                <div className="font-medium">{text.label}</div>
                <div className="truncate font-mono text-xs text-muted-foreground">
                  {problem.url}
                </div>
                {problem.detail && <div className="mt-0.5 text-xs">{problem.detail}</div>}
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
