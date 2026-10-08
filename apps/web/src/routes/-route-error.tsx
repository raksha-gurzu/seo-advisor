import type { ErrorComponentProps } from "@tanstack/react-router";
import { ServerCrash } from "lucide-react";

import { ApiError } from "@/shared/lib/api";
import { Button } from "@/shared/ui/button";
import { EmptyState } from "@/shared/ui/empty-state";

/** Shown when a route's data cannot load. It says what failed; it never hides it. */
export function RouteError({ error, reset }: ErrorComponentProps) {
  const api = error instanceof ApiError ? error : null;
  const title =
    api?.status === 404
      ? "Not found"
      : api
        ? "The API answered with an error"
        : "The API cannot be reached";
  return (
    <EmptyState
      icon={<ServerCrash />}
      title={title}
      action={
        <Button variant="outline" onClick={reset}>
          Try again
        </Button>
      }
    >
      <p>{error instanceof Error ? error.message : String(error)}</p>
      {api?.requestId && <p className="mt-1 font-mono text-xs">request {api.requestId}</p>}
      {!api && (
        <p className="mt-1">
          Start the API and the database with <code className="font-mono text-xs">make dev</code>.
        </p>
      )}
    </EmptyState>
  );
}
