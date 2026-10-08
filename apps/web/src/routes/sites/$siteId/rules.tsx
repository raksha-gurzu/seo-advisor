import { useSuspenseQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";

import { RulesView } from "@/features/inventory/rules-view";
import { siteQuery } from "@/features/sites/queries";

export const Route = createFileRoute("/sites/$siteId/rules")({
  component: RulesPage,
});

function RulesPage() {
  const { siteId } = Route.useParams();
  const { data: site } = useSuspenseQuery(siteQuery(siteId));
  return <RulesView site={site} />;
}
