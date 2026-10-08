import { createFileRoute } from "@tanstack/react-router";

import { ActivityView } from "@/features/inventory/activity-view";
import { DiscoveryEmpty } from "@/features/inventory/discovery-empty";
import { useDiscovery } from "@/features/inventory/queries";

export const Route = createFileRoute("/sites/$siteId/activity")({
  component: ActivityPage,
});

function ActivityPage() {
  const { siteId } = Route.useParams();
  const { data: run } = useDiscovery(siteId);
  if (!run) return <DiscoveryEmpty siteId={siteId} title="No requests yet" />;
  return <ActivityView run={run} />;
}
