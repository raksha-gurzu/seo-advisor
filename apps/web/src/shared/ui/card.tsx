import type { ComponentProps } from "react";

import { cn } from "@/shared/lib/utils";

export function Card({ className, ...props }: ComponentProps<"section">) {
  return (
    <section
      className={cn("rounded-xl border bg-card text-card-foreground shadow-xs", className)}
      {...props}
    />
  );
}

export function CardHeader({ className, ...props }: ComponentProps<"header">) {
  return (
    <header
      className={cn("flex items-start justify-between gap-4 px-5 pt-4 pb-3", className)}
      {...props}
    />
  );
}

export function CardTitle({ className, children, ...props }: ComponentProps<"h2">) {
  return (
    <h2 className={cn("text-sm font-semibold tracking-tight", className)} {...props}>
      {children}
    </h2>
  );
}

export function CardDescription({ className, ...props }: ComponentProps<"p">) {
  return <p className={cn("text-[13px] text-muted-foreground", className)} {...props} />;
}

export function CardContent({ className, ...props }: ComponentProps<"div">) {
  return <div className={cn("px-5 pb-5", className)} {...props} />;
}
