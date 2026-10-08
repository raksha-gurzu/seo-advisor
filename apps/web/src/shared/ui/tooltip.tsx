import { Tooltip as TooltipPrimitive } from "radix-ui";
import type { ComponentProps, ReactNode } from "react";

import { cn } from "@/shared/lib/utils";

export const TooltipProvider = TooltipPrimitive.Provider;

/** A short hint on hover or focus. The trigger must be focusable. */
export function Tooltip({
  content,
  children,
  side = "top",
  className,
}: {
  content: ReactNode;
  children: ReactNode;
  side?: ComponentProps<typeof TooltipPrimitive.Content>["side"];
  className?: string;
}) {
  return (
    <TooltipPrimitive.Root>
      <TooltipPrimitive.Trigger asChild>{children}</TooltipPrimitive.Trigger>
      <TooltipPrimitive.Portal>
        <TooltipPrimitive.Content
          side={side}
          sideOffset={6}
          className={cn(
            "z-50 max-w-sm animate-in rounded-md bg-foreground px-2.5 py-1.5 text-xs text-background shadow-md fade-in-0 zoom-in-95",
            className,
          )}
        >
          {content}
        </TooltipPrimitive.Content>
      </TooltipPrimitive.Portal>
    </TooltipPrimitive.Root>
  );
}

/** Text with a tooltip. A button, so keyboard users can reach the hint too. */
export function TooltipText({
  content,
  className,
  children,
}: {
  content: ReactNode;
  className?: string;
  children: ReactNode;
}) {
  return (
    <Tooltip content={content}>
      <button type="button" className={cn("cursor-default text-left", className)}>
        {children}
      </button>
    </Tooltip>
  );
}
