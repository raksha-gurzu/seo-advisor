import { useQuery } from "@tanstack/react-query";
import { ArrowRight, FlaskConical, LoaderCircle } from "lucide-react";
import { Fragment, useEffect, useState } from "react";

import { pageTypeColor } from "@/features/inventory/page-types";
import { pageTypeQuery, useDiscovery } from "@/features/inventory/queries";
import type { Site } from "@/shared/lib/api";
import { formatCount, humanize } from "@/shared/lib/format";
import { cn } from "@/shared/lib/utils";
import { Badge } from "@/shared/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/ui/card";
import { Input } from "@/shared/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";

/** "/blog/*" with each "*" in the accent colour, so the wildcard parts stand out. */
function Pattern({ pattern }: { pattern: string }) {
  return (
    <code className="font-mono text-[13px]">
      {pattern.split("*").map((part, index) => (
        <Fragment key={index}>
          {index > 0 && (
            <span className="rounded bg-accent px-0.5 font-semibold text-primary">*</span>
          )}
          {part}
        </Fragment>
      ))}
    </code>
  );
}

function useDebounced<T>(value: T, ms: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = window.setTimeout(() => setDebounced(value), ms);
    return () => window.clearTimeout(timer);
  }, [value, ms]);
  return debounced;
}

export function RulesView({ site }: { site: Site }) {
  const [url, setUrl] = useState(`${site.base_url}/blog/`);
  const debounced = useDebounced(url.trim(), 250);
  const match = useQuery({ ...pageTypeQuery(site.id, debounced), enabled: debounced !== "" });
  const { data: run } = useDiscovery(site.id);

  const counts = new Map<string, number>();
  for (const page of run?.inventory.pages ?? []) {
    counts.set(page.page_type, (counts.get(page.page_type) ?? 0) + 1);
  }
  const matchedIndex = match.data?.rule_index ?? null;

  return (
    <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_380px]">
      <Card className="overflow-hidden">
        <CardHeader>
          <div>
            <CardTitle>Page-type rules</CardTitle>
            <CardDescription>
              The first rule that matches the URL path wins. A <Pattern pattern="*" /> is exactly
              one path part.
            </CardDescription>
          </div>
          <Badge>{site.page_types.length} rules</Badge>
        </CardHeader>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12 pl-5">#</TableHead>
                <TableHead>Pattern</TableHead>
                <TableHead>Page type</TableHead>
                <TableHead className="pr-5 text-right">Pages in last run</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {site.page_types.map((rule, index) => (
                <TableRow
                  key={`${rule.pattern}-${index}`}
                  data-state={matchedIndex === index ? "selected" : undefined}
                  className={cn(matchedIndex === index && "shadow-[inset_3px_0_0_var(--primary)]")}
                >
                  <TableCell className="pl-5 text-muted-foreground tabular-nums">
                    {index + 1}
                  </TableCell>
                  <TableCell>
                    <Pattern pattern={rule.pattern} />
                  </TableCell>
                  <TableCell>
                    <span className="inline-flex items-center gap-2 text-[13px] whitespace-nowrap">
                      <span
                        className="size-2 rounded-full"
                        style={{ background: pageTypeColor(site.page_types, rule.page_type) }}
                      />
                      {humanize(rule.page_type)}
                    </span>
                  </TableCell>
                  <TableCell className="pr-5 text-right tabular-nums">
                    {run ? formatCount(counts.get(rule.page_type) ?? 0) : "—"}
                  </TableCell>
                </TableRow>
              ))}
              <TableRow className="text-muted-foreground">
                <TableCell className="pl-5">—</TableCell>
                <TableCell className="text-[13px] italic">no rule matches</TableCell>
                <TableCell>
                  <span className="inline-flex items-center gap-2 text-[13px] whitespace-nowrap">
                    <span
                      className="size-2 rounded-full"
                      style={{ background: "var(--cat-other)" }}
                    />
                    Other
                  </span>
                </TableCell>
                <TableCell className="pr-5 text-right tabular-nums">
                  {run ? formatCount(counts.get("other") ?? 0) : "—"}
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
        <p className="border-t px-5 py-3 text-xs text-muted-foreground">
          The rules come from the site file in <code className="font-mono">infra/sites/</code>.
          Change the file, then run <code className="font-mono">make seed</code>.
        </p>
      </Card>

      <Card className="h-fit">
        <CardHeader>
          <div>
            <CardTitle className="flex items-center gap-2">
              <FlaskConical className="size-4 text-primary" /> Test a URL
            </CardTitle>
            <CardDescription>
              See which rule gives a URL its page type. Nothing is fetched.
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            aria-label="URL to test"
            className="font-mono text-[13px]"
            spellCheck={false}
          />
          <div aria-live="polite" className="min-h-28 rounded-lg border bg-muted/40 p-4 text-sm">
            {match.isFetching && !match.data ? (
              <LoaderCircle className="size-4 animate-spin text-muted-foreground" />
            ) : match.isError ? (
              <p className="text-critical">{match.error.message}</p>
            ) : match.data ? (
              <dl className="space-y-3">
                <div>
                  <dt className="text-xs text-muted-foreground">Path compared</dt>
                  <dd className="font-mono text-[13px] break-all">{match.data.path}</dd>
                </div>
                <div className="flex items-center gap-2">
                  <ArrowRight className="size-4 text-muted-foreground" />
                  <span
                    className="size-2.5 rounded-full"
                    style={{ background: pageTypeColor(site.page_types, match.data.page_type) }}
                  />
                  <span className="text-base font-semibold">{humanize(match.data.page_type)}</span>
                </div>
                <dd className="text-xs text-muted-foreground">
                  {match.data.rule_index === null || match.data.rule_index === undefined
                    ? "No rule matches, so the page type is “other”."
                    : `Rule #${match.data.rule_index + 1} (${match.data.pattern ?? ""}) is the first match.`}
                </dd>
              </dl>
            ) : (
              <p className="text-muted-foreground">Enter a URL.</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
