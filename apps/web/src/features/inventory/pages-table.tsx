import {
  createColumnHelper,
  createSortedRowModel,
  rowSortingFeature,
  sortFn_alphanumeric,
  sortFn_text,
  tableFeatures,
  useTable,
} from "@tanstack/react-table";
import { ArrowDown, ArrowUp, ArrowUpDown, ExternalLink, Search, X } from "lucide-react";
import { useMemo } from "react";

import { pageTypeColor } from "@/features/inventory/page-types";
import type { DiscoveredPage, PageTypeRule } from "@/shared/lib/api";
import { fileOf, formatCount, formatDate, humanize, pathOf } from "@/shared/lib/format";
import { cn } from "@/shared/lib/utils";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { Input } from "@/shared/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";
import { TooltipText } from "@/shared/ui/tooltip";

const features = tableFeatures({
  rowSortingFeature,
  sortedRowModel: createSortedRowModel(),
  sortFns: { alphanumeric: sortFn_alphanumeric, text: sortFn_text },
});
const helper = createColumnHelper<typeof features, DiscoveredPage>();

/** The table columns. Cells read the rules only for the page-type colour. */
function pageColumns(rules: PageTypeRule[]) {
  return helper.columns([
    helper.accessor((page) => pathOf(page.url), {
      id: "path",
      header: "Path",
      sortFn: "alphanumeric",
      cell: (info) => (
        <a
          href={info.row.original.url}
          target="_blank"
          rel="noreferrer noopener"
          className="group/link inline-flex max-w-full items-center gap-1.5 font-mono text-[13px] hover:text-primary"
        >
          <span className="truncate">{info.getValue()}</span>
          <ExternalLink className="size-3 shrink-0 opacity-0 transition-opacity group-hover/link:opacity-100" />
        </a>
      ),
    }),
    helper.accessor("page_type", {
      header: "Page type",
      sortFn: "text",
      cell: (info) => (
        <span className="inline-flex items-center gap-2 text-[13px] whitespace-nowrap">
          <span
            className="size-2 rounded-full"
            style={{ background: pageTypeColor(rules, info.getValue()) }}
          />
          {humanize(info.getValue())}
        </span>
      ),
    }),
    helper.accessor("lastmod", {
      header: "Last modified",
      sortFn: "text",
      cell: (info) =>
        info.getValue() ? (
          <span className="text-[13px] whitespace-nowrap tabular-nums">
            {formatDate(info.getValue())}
          </span>
        ) : (
          <TooltipText
            content="The sitemap gives no <lastmod> for this URL."
            className="text-muted-foreground"
          >
            —
          </TooltipText>
        ),
    }),
    helper.accessor((page) => fileOf(page.sitemap), {
      id: "sitemap",
      header: "Sitemap",
      sortFn: "text",
      cell: (info) => (
        <TooltipText
          content={info.row.original.sitemap}
          className="font-mono text-xs text-muted-foreground"
        >
          {info.getValue()}
        </TooltipText>
      ),
    }),
  ]);
}

export function PagesTable({
  pages,
  rules,
  query,
  onQuery,
  type,
  onClearType,
  total,
}: {
  pages: DiscoveredPage[];
  rules: PageTypeRule[];
  query: string;
  onQuery: (query: string) => void;
  type: string | undefined;
  onClearType: () => void;
  total: number;
}) {
  const columns = useMemo(() => pageColumns(rules), [rules]);

  const table = useTable({
    features,
    columns,
    data: pages,
    initialState: { sorting: [{ id: "path", desc: false }] },
    enableSortingRemoval: false,
  });

  return (
    <Card className="overflow-hidden">
      <div className="flex flex-col gap-3 border-b px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative w-full sm:max-w-xs">
          <Search className="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={query}
            onChange={(event) => onQuery(event.target.value)}
            placeholder="Filter by path…"
            aria-label="Filter pages by path"
            className="h-8 pl-8"
          />
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          {type && (
            <Button variant="outline" size="sm" onClick={onClearType} className="h-7">
              {humanize(type)} <X className="size-3" />
            </Button>
          )}
          <span className="tabular-nums">
            {formatCount(pages.length)} of {formatCount(total)} pages
          </span>
        </div>
      </div>
      <div className="max-h-[560px] overflow-auto">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((group) => (
              <TableRow key={group.id}>
                {group.headers.map((header) => {
                  const sorted = header.column.getIsSorted();
                  const Icon =
                    sorted === "asc" ? ArrowUp : sorted === "desc" ? ArrowDown : ArrowUpDown;
                  return (
                    <TableHead
                      key={header.id}
                      aria-sort={
                        sorted === "asc" ? "ascending" : sorted === "desc" ? "descending" : "none"
                      }
                      className={cn(header.column.id === "path" && "w-1/2 pl-4")}
                    >
                      <button
                        type="button"
                        onClick={header.column.getToggleSortingHandler()}
                        className="inline-flex items-center gap-1 hover:text-foreground"
                      >
                        <table.FlexRender header={header} />
                        <Icon className={cn("size-3", !sorted && "opacity-40")} />
                      </button>
                    </TableHead>
                  );
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.map((row) => (
              <TableRow key={row.id}>
                {row.getAllCells().map((cell) => (
                  <TableCell
                    key={cell.id}
                    className={cn(cell.column.id === "path" && "max-w-0 pl-4")}
                  >
                    <table.FlexRender cell={cell} />
                  </TableCell>
                ))}
              </TableRow>
            ))}
            {pages.length === 0 && (
              <TableRow>
                <TableCell colSpan={4} className="h-24 text-center text-muted-foreground">
                  No page matches this filter.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </Card>
  );
}
