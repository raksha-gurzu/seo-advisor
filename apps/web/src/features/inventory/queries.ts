import {
  queryOptions,
  skipToken,
  useMutation,
  useMutationState,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { toast } from "sonner";

import { api, ApiError, type DiscoveryRun, unwrap } from "@/shared/lib/api";
import { formatMs } from "@/shared/lib/format";

/**
 * The last discovery of a site lives only in the query cache (this browser tab).
 * Slice 2b saves pages in the database; then this reads the stored inventory.
 */
export const discoveryKey = (siteId: string) => ["discovery", siteId] as const;

export function useDiscovery(siteId: string) {
  return useQuery<DiscoveryRun>({
    queryKey: discoveryKey(siteId),
    queryFn: skipToken, // filled only by useRunDiscovery
    staleTime: Infinity,
    gcTime: Infinity,
  });
}

export function useRunDiscovery() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: ["discovery"],
    mutationFn: async (siteId: string) =>
      unwrap(
        await api.POST("/api/v1/sites/{site_id}/discoveries", {
          params: { path: { site_id: siteId } },
        }),
      ),
    onSuccess: (run) => {
      queryClient.setQueryData(discoveryKey(run.site_id), run);
      const { pages, problems } = run.inventory;
      const sent = run.requests.filter((event) => typeof event.status === "number").length;
      const requests = sent === 1 ? "1 request sent" : `${sent} requests sent`;
      toast.success(`Found ${pages.length} pages in ${formatMs(run.duration_ms)}`, {
        description:
          problems.length === 0
            ? `${requests}, no problems.`
            : `${requests}, ${problems.length} problems.`,
      });
    },
    onError: (error) => {
      const requestId = error instanceof ApiError ? error.requestId : undefined;
      toast.error("Discovery failed", {
        description: requestId ? `${error.message} (request ${requestId})` : error.message,
      });
    },
  });
}

/** True while a discovery of this site runs (from any button or the palette). */
export function useIsDiscovering(siteId: string): boolean {
  const running = useMutationState({
    filters: { mutationKey: ["discovery"], status: "pending" },
    select: (mutation) => mutation.state.variables,
  });
  return running.includes(siteId);
}

export const pageTypeQuery = (siteId: string, url: string) =>
  queryOptions({
    queryKey: ["page-type", siteId, url],
    queryFn: async () =>
      unwrap(
        await api.GET("/api/v1/sites/{site_id}/page-type", {
          params: { path: { site_id: siteId }, query: { url } },
        }),
      ),
    staleTime: Infinity,
  });
