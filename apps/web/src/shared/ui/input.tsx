import type { ComponentProps } from "react";

import { cn } from "@/shared/lib/utils";

export function Input({ className, type = "text", ...props }: ComponentProps<"input">) {
  return (
    <input
      type={type}
      className={cn(
        "h-9 w-full min-w-0 rounded-md border border-input/45 bg-card px-3 text-sm shadow-xs transition-[border-color,box-shadow] outline-none placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/30 disabled:opacity-50 dark:bg-input/10",
        className,
      )}
      {...props}
    />
  );
}
