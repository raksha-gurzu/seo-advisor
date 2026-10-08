import { useSuspenseQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";

import { DiscoveryEmpty } from "@/features/inventory/discovery-empty";
import { InventoryView } from "@/features/inventory/inventory-view";
import { useDiscovery, useIsDiscovering } from "@/features/inventory/queries";
import { siteQuery } from "@/features/sites/queries";
import { Skeleton } from "@/shared/ui/skeleton";

type InventorySearch = { type?: string | undefined; q?: string | undefined };

export const Route = createFileRoute("/sites/$siteId/")({
  validateSearch: (search: Record<string, unknown>): InventorySearch => ({
    ...(typeof search.type === "string" && search.type !== "" ? { type: search.type } : {}),
    ...(typeof search.q === "string" && search.q !== "" ? { q: search.q } : {}),
  }),
  component: InventoryPage,
});

function InventoryPage() {
  const { siteId } = Route.useParams();
  const { type, q = "" } = Route.useSearch();
  const { data: site } = useSuspenseQuery(siteQuery(siteId));
  const { data: run } = useDiscovery(siteId);
  const running = useIsDiscovering(siteId);

  if (!run && running) return <InventorySkeleton />;
  if (!run) return <DiscoveryEmpty siteId={siteId} title="Run the first discovery" />;
  return <InventoryView site={site} run={run} type={type} query={q} />;
}

function InventorySkeleton() {
  return (
    <div className="space-y-5" aria-busy>
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {Array.from({ length: 4 }, (_, index) => (
          <Skeleton key={index} className="h-[92px] rounded-xl" />
        ))}
      </div>
      <Skeleton className="h-28 rounded-xl" />
      <Skeleton className="h-96 rounded-xl" />
    </div>
  );
}
