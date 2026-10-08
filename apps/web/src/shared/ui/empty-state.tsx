import type { ReactNode } from "react";

import { cn } from "@/shared/lib/utils";

export function EmptyState({
  icon,
  title,
  children,
  action,
  className,
}: {
  icon: ReactNode;
  title: string;
  children?: ReactNode;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-center rounded-xl border border-dashed bg-card/50 px-6 py-12 text-center",
        className,
      )}
    >
      <div className="mb-4 flex size-11 items-center justify-center rounded-xl border bg-card text-primary shadow-xs [&_svg]:size-5">
        {icon}
      </div>
      <h2 className="text-base font-semibold tracking-tight">{title}</h2>
      {children && <div className="mt-1.5 max-w-md text-sm text-muted-foreground">{children}</div>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}
