import { useQueryClient, useSuspenseQuery } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { ArrowRight, Globe } from "lucide-react";

import { discoveryKey } from "@/features/inventory/queries";
import { sitesQuery } from "@/features/sites/queries";
import { SiteMark } from "@/features/sites/site-mark";
import type { DiscoveryRun } from "@/shared/lib/api";
import { formatCount, formatRelative, hostOf } from "@/shared/lib/format";
import { Badge } from "@/shared/ui/badge";
import { Card } from "@/shared/ui/card";
import { EmptyState } from "@/shared/ui/empty-state";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";
import { TooltipText } from "@/shared/ui/tooltip";

export function SitesTable() {
  const { data: sites } = useSuspenseQuery(sitesQuery());
  const queryClient = useQueryClient();

  if (sites.length === 0) {
    return (
      <EmptyState icon={<Globe />} title="No sites yet">
        Add a site file in <code className="font-mono text-xs">infra/sites/</code>, then run{" "}
        <code className="font-mono text-xs">make seed</code>.
      </EmptyState>
    );
  }

  return (
    <Card className="overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="pl-5">Site</TableHead>
            <TableHead>Language</TableHead>
            <TableHead className="text-right">Page-type rules</TableHead>
            <TableHead>Last discovery</TableHead>
            <TableHead className="w-10 pr-5" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {sites.map((site) => {
            const host = hostOf(site.base_url);
            const run = queryClient.getQueryData<DiscoveryRun>(discoveryKey(site.id));
            return (
              <TableRow key={site.id} className="group relative">
                <TableCell className="py-3 pl-5">
                  <div className="flex items-center gap-3">
                    <SiteMark host={host} />
                    <div className="min-w-0">
                      <Link
                        to="/sites/$siteId"
                        params={{ siteId: site.id }}
                        className="font-medium after:absolute after:inset-0 hover:underline"
                      >
                        {host}
                      </Link>
                      <div className="text-xs text-muted-foreground">{site.tenant_name}</div>
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <Badge className="font-mono uppercase">{site.language}</Badge>
                </TableCell>
                <TableCell className="text-right tabular-nums">
                  {formatCount(site.page_types.length)}
                </TableCell>
                <TableCell>
                  {run ? (
                    <span className="text-sm">
                      <span className="font-medium tabular-nums">
                        {formatCount(run.inventory.pages.length)}
                      </span>{" "}
                      pages{" "}
                      <span className="text-muted-foreground">
                        · {formatRelative(run.started_at)}
                      </span>
                    </span>
                  ) : (
                    <TooltipText
                      content="Results stay in this browser tab until pages are saved (slice 2b)."
                      className="relative z-10 text-sm text-muted-foreground"
                    >
                      Not run in this tab
                    </TooltipText>
                  )}
                </TableCell>
                <TableCell className="pr-5 text-muted-foreground">
                  <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5 group-hover:text-foreground" />
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </Card>
  );
}
