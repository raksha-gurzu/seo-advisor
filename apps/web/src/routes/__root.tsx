import type { QueryClient } from "@tanstack/react-query";
import { createRootRouteWithContext, Link } from "@tanstack/react-router";
import { Compass } from "lucide-react";

import { AppShell } from "@/app/app-shell";
import { Button } from "@/shared/ui/button";
import { EmptyState } from "@/shared/ui/empty-state";

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()({
  component: AppShell,
  notFoundComponent: () => (
    <EmptyState
      icon={<Compass />}
      title="This page does not exist"
      action={
        <Button asChild variant="outline">
          <Link to="/sites">Go to sites</Link>
        </Button>
      }
    />
  ),
});
