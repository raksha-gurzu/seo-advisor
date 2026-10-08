import { queryOptions } from "@tanstack/react-query";

import { api, unwrap } from "@/shared/lib/api";

export const sitesQuery = () =>
  queryOptions({
    queryKey: ["sites"],
    queryFn: async () => unwrap(await api.GET("/api/v1/sites")),
  });

export const siteQuery = (siteId: string) =>
  queryOptions({
    queryKey: ["sites", siteId],
    queryFn: async () =>
      unwrap(await api.GET("/api/v1/sites/{site_id}", { params: { path: { site_id: siteId } } })),
  });

export const healthQuery = () =>
  queryOptions({
    queryKey: ["health"],
    queryFn: async () => unwrap(await api.GET("/health")),
    refetchInterval: 15_000,
    retry: false,
  });
