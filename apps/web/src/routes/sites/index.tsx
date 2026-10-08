import { createFileRoute } from "@tanstack/react-router";

import { sitesQuery } from "@/features/sites/queries";
import { SitesTable } from "@/features/sites/sites-table";
import { StageStrip } from "@/features/sites/stage-strip";
import { PageHeader } from "@/shared/ui/page-header";
import { RouteError } from "@/routes/-route-error";

export const Route = createFileRoute("/sites/")({
  loader: ({ context }) => context.queryClient.ensureQueryData(sitesQuery()),
  errorComponent: RouteError,
  component: SitesPage,
});

function SitesPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Sites"
        description="The sites that seo-advisor watches. Open a site to read its robots.txt and sitemaps (live, read-only)."
      />
      <section className="space-y-3">
        <h2 className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
          Where the platform is
        </h2>
        <StageStrip />
      </section>
      <SitesTable />
    </div>
  );
}
