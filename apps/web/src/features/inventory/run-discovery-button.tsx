import { LoaderCircle, Play, RotateCw } from "lucide-react";

import { useDiscovery, useIsDiscovering, useRunDiscovery } from "@/features/inventory/queries";
import { Button } from "@/shared/ui/button";

export function RunDiscoveryButton({ siteId, size }: { siteId: string; size?: "default" | "lg" }) {
  const run = useRunDiscovery();
  const running = useIsDiscovering(siteId);
  const { data } = useDiscovery(siteId);
  return (
    <Button size={size} onClick={() => run.mutate(siteId)} disabled={running}>
      {running ? <LoaderCircle className="animate-spin" /> : data ? <RotateCw /> : <Play />}
      {running ? "Discovering…" : data ? "Run again" : "Run discovery"}
    </Button>
  );
}
