import { type ApiClient, createApiClient } from "api-client";
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import { afterAll, afterEach, beforeAll, describe, expect, it } from "vitest";

import { ApiError, unwrap } from "@/shared/lib/api";

const BASE = "http://api.test";
const server = setupServer();
let client: ApiClient;

beforeAll(() => {
  server.listen({ onUnhandledFrame: "error" });
  // openapi-fetch keeps the fetch it sees at creation, so create it after MSW starts.
  client = createApiClient(BASE);
});
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe("unwrap", () => {
  it("returns the data of a 2xx answer", async () => {
    server.use(http.get(`${BASE}/health`, () => HttpResponse.json({ status: "ok" })));
    expect(unwrap(await client.GET("/health"))).toEqual({ status: "ok" });
  });

  it("turns a problem document into an ApiError with the request ID", async () => {
    server.use(
      http.get(`${BASE}/api/v1/sites/:id`, () =>
        HttpResponse.json(
          { title: "Not Found", status: 404, detail: "site x does not exist", request_id: "r-1" },
          { status: 404, headers: { "content-type": "application/problem+json" } },
        ),
      ),
    );
    const result = await client.GET("/api/v1/sites/{site_id}", {
      params: { path: { site_id: "x" } },
    });
    expect(() => unwrap(result)).toThrow(ApiError);
    expect(() => unwrap(result)).toThrow("site x does not exist");
    try {
      unwrap(result);
    } catch (error) {
      expect((error as ApiError).requestId).toBe("r-1");
      expect((error as ApiError).status).toBe(404);
    }
  });
});
