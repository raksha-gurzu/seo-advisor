import { useNavigate } from "@tanstack/react-router";
import { AlertTriangle, FileStack, FileText, Shapes } from "lucide-react";
import { useMemo } from "react";

import { pageTypeOrder } from "@/features/inventory/page-types";
import { PagesTable } from "@/features/inventory/pages-table";
import { ProblemsList } from "@/features/inventory/problems-list";
import { TypeDistribution } from "@/features/inventory/type-distribution";
import type { DiscoveryRun, Site } from "@/shared/lib/api";
import { fileOf, formatCount, formatMs, formatRelative } from "@/shared/lib/format";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/ui/card";
import { Stat } from "@/shared/ui/stat";

export function InventoryView({
  site,
  run,
  type,
  query,
}: {
  site: Site;
  run: DiscoveryRun;
  type: string | undefined;
  query: string;
}) {
  const navigate = useNavigate({ from: "/sites/$siteId/" });
  const { pages, problems, sitemaps_read } = run.inventory;

  const counts = useMemo(() => {
    const byType = new Map<string, number>();
    for (const page of pages) byType.set(page.page_type, (byType.get(page.page_type) ?? 0) + 1);
    return pageTypeOrder(site.page_types, byType.keys()).map((name) => ({
      type: name,
      count: byType.get(name) ?? 0,
    }));
  }, [pages, site.page_types]);

  const visible = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return pages.filter(
      (page) =>
        (type === undefined || page.page_type === type) &&
        (needle === "" || page.url.toLowerCase().includes(needle)),
    );
  }, [pages, type, query]);

  const setSearch = (next: { type?: string | undefined; q?: string | undefined }) =>
    void navigate({ search: (prev) => ({ ...prev, ...next }), replace: true });

  const typesFound = counts.filter((item) => item.count > 0).length;

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Stat
          label="Pages"
          value={formatCount(pages.length)}
          icon={<FileText />}
          hint="URLs in the sitemaps"
        />
        <Stat
          label="Sitemaps read"
          value={formatCount(sitemaps_read.length)}
          icon={<FileStack />}
          hint={sitemaps_read.map(fileOf).join(", ") || "none"}
        />
        <Stat
          label="Page types"
          value={formatCount(typesFound)}
          icon={<Shapes />}
          hint={`${site.page_types.length} rules`}
        />
        <Stat
          label="Problems"
          value={formatCount(problems.length)}
          icon={<AlertTriangle />}
          tone={problems.length === 0 ? "success" : "warning"}
          hint={problems.length === 0 ? "none found" : "see the list below"}
        />
      </div>

      <Card>
        <CardHeader>
          <div>
            <CardTitle>Pages by type</CardTitle>
            <CardDescription>Select a type to filter the table.</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <TypeDistribution
            counts={counts}
            total={pages.length}
            rules={site.page_types}
            selected={type}
            onSelect={(next) => setSearch({ type: next })}
          />
        </CardContent>
      </Card>

      <ProblemsList problems={problems} />

      <PagesTable
        pages={visible}
        total={pages.length}
        rules={site.page_types}
        query={query}
        onQuery={(next) => setSearch({ q: next === "" ? undefined : next })}
        type={type}
        onClearType={() => setSearch({ type: undefined })}
      />

      <p className="text-xs text-muted-foreground">
        Discovered {formatRelative(run.started_at)} in {formatMs(run.duration_ms)}. The result is
        kept in this browser tab only; saved pages come with slice 2b.
      </p>
    </div>
  );
}
