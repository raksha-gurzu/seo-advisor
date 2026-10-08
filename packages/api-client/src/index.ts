// The only way the web app calls the API (CLAUDE.md, Code).
// schema.d.ts is generated from the API's OpenAPI document: `mise run gen-client`.
import createClient from "openapi-fetch";

import type { components, paths } from "./schema";

export type Schemas = components["schemas"];

/** A typed API client. `baseUrl` is "" in the browser: Vite sends /api to the API. */
export function createApiClient(baseUrl: string) {
  return createClient<paths>({ baseUrl });
}

export type ApiClient = ReturnType<typeof createApiClient>;
