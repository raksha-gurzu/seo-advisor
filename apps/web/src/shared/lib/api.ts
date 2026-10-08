import { createApiClient, type Schemas } from "api-client";

/** Same origin: in development Vite sends /api and /health to the API. */
export const api = createApiClient("");

export type Site = Schemas["SiteRecord"];
export type DiscoveryRun = Schemas["DiscoveryRun"];
export type DiscoveredPage = Schemas["DiscoveredPage"];
export type InventoryProblem = Schemas["InventoryProblem"];
export type FetchEvent = Schemas["FetchEvent"];
export type PageTypeMatch = Schemas["PageTypeMatch"];
export type PageTypeRule = Schemas["PageTypeRule"];

/** An API answer that is not 2xx. `detail` comes from the RFC 9457 problem document. */
export class ApiError extends Error {
  readonly status: number;
  readonly requestId: string | undefined;

  constructor(status: number, detail: string, requestId: string | undefined) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.requestId = requestId;
  }
}

type Problem = { detail?: unknown; request_id?: unknown };

/** The data of an openapi-fetch result, or an ApiError. Never a silent default. */
export function unwrap<T>(result: { data?: T; error?: unknown; response: Response }): T {
  if (result.data !== undefined && result.response.ok) return result.data;
  const problem = (result.error ?? {}) as Problem;
  const detail =
    typeof problem.detail === "string" ? problem.detail : `HTTP ${result.response.status}`;
  const requestId =
    typeof problem.request_id === "string"
      ? problem.request_id
      : (result.response.headers.get("x-request-id") ?? undefined);
  throw new ApiError(result.response.status, detail, requestId);
}
