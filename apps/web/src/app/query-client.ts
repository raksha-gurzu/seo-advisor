import { QueryClient } from "@tanstack/react-query";

import { ApiError } from "@/shared/lib/api";

export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        // Retry network errors once; a 4xx answer will not change on a retry.
        retry: (count, error) => !(error instanceof ApiError && error.status < 500) && count < 1,
      },
    },
  });
}
