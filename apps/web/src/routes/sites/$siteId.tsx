import { useSuspenseQuery } from "@tanstack/react-query";
import { createFileRoute, Link, Outlet } from "@tanstack/react-router";
import { ExternalLink } from "lucide-react";
import type { ReactNode } from "react";

import { useDiscovery, useIsDiscovering } from "@/features/inventory/queries";
import { RunDiscoveryButton } from "@/features/inventory/run-discovery-button";
import { siteQuery } from "@/features/sites/queries";
import { SiteMark } from "@/features/sites/site-mark";
import { formatCount, hostOf } from "@/shared/lib/format";
import { Badge } from "@/shared/ui/badge";
import { RouteError } from "@/routes/-route-error";

export const Route = createFileRoute("/sites/$siteId")({
  loader: ({ context, params }) => context.queryClient.ensureQueryData(siteQuery(params.siteId)),
  errorComponent: RouteError,
  component: SiteLayout,
});

function SiteLayout() {
  const { siteId } = Route.useParams();
  const { data: site } = useSuspenseQuery(siteQuery(siteId));
  const { data: run } = useDiscovery(siteId);
  const running = useIsDiscovering(siteId);
  const host = hostOf(site.base_url);

  return (
    <div className="space-y-6">
      <nav aria-label="Breadcrumb" className="text-xs text-muted-foreground">
        <Link to="/sites" className="hover:text-foreground">
          Sites
        </Link>
        <span className="mx-1.5">/</span>
        <span className="text-foreground">{host}</span>
      </nav>

      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex min-w-0 items-center gap-3.5">
          <SiteMark host={host} className="size-11 rounded-xl text-lg" />
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="truncate text-2xl font-semibold tracking-tight">{host}</h1>
              <Badge className="font-mono uppercase">{site.language}</Badge>
              <Badge tone="primary">{site.tenant_name}</Badge>
            </div>
            <a
              href={site.base_url}
              target="_blank"
              rel="noreferrer noopener"
              className="mt-0.5 inline-flex items-center gap-1 font-mono text-xs text-muted-foreground hover:text-primary"
            >
              {site.base_url} <ExternalLink className="size-3" />
            </a>
          </div>
        </div>
        <RunDiscoveryButton siteId={siteId} />
      </header>

      <div className="relative">
        <nav className="flex gap-1 overflow-x-auto border-b" aria-label="Site sections">
          <Tab to="/sites/$siteId" siteId={siteId} exact count={run?.inventory.pages.length}>
            Inventory
          </Tab>
          <Tab to="/sites/$siteId/rules" siteId={siteId} count={site.page_types.length}>
            Rules
          </Tab>
          <Tab to="/sites/$siteId/activity" siteId={siteId} count={run?.requests.length}>
            Activity
          </Tab>
        </nav>
        <span className="sr-only" aria-live="polite">
          {running ? "Discovery running" : ""}
        </span>
        {running && (
          <div className="absolute inset-x-0 -bottom-px h-0.5 overflow-hidden" aria-hidden>
            <div className="h-full w-1/3 animate-[slide_1.1s_ease-in-out_infinite] rounded-full bg-primary" />
          </div>
        )}
      </div>

      <Outlet />
    </div>
  );
}

function Tab({
  to,
  siteId,
  exact = false,
  count,
  children,
}: {
  to: "/sites/$siteId" | "/sites/$siteId/rules" | "/sites/$siteId/activity";
  siteId: string;
  exact?: boolean;
  count: number | undefined;
  children: ReactNode;
}) {
  return (
    <Link
      to={to}
      params={{ siteId }}
      activeOptions={{ exact, includeSearch: false }}
      className="-mb-px flex items-center gap-2 border-b-2 border-transparent px-3 pt-1 pb-2.5 text-sm text-muted-foreground transition-colors hover:text-foreground data-[status=active]:border-primary data-[status=active]:font-medium data-[status=active]:text-foreground"
    >
      {children}
      {count !== undefined && (
        <span className="rounded-full bg-muted px-1.5 py-px text-[11px] text-muted-foreground tabular-nums">
          {formatCount(count)}
        </span>
      )}
    </Link>
  );
}
