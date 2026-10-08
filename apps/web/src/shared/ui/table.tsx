import type { ComponentProps } from "react";

import { cn } from "@/shared/lib/utils";

export function Table({ className, ...props }: ComponentProps<"table">) {
  return <table className={cn("w-full caption-bottom text-sm", className)} {...props} />;
}

export function TableHeader({ className, ...props }: ComponentProps<"thead">) {
  return (
    <thead
      className={cn(
        "sticky top-0 z-10 bg-card/95 backdrop-blur-sm [&_tr]:border-b [&_tr]:hover:bg-transparent",
        className,
      )}
      {...props}
    />
  );
}

export function TableBody({ className, ...props }: ComponentProps<"tbody">) {
  return <tbody className={cn("[&_tr:last-child]:border-0", className)} {...props} />;
}

export function TableRow({ className, ...props }: ComponentProps<"tr">) {
  return (
    <tr
      className={cn(
        "border-b transition-colors hover:bg-muted/60 data-[state=selected]:bg-accent",
        className,
      )}
      {...props}
    />
  );
}

export function TableHead({ className, ...props }: ComponentProps<"th">) {
  return (
    <th
      className={cn(
        "h-9 px-3 text-left align-middle text-xs font-medium whitespace-nowrap text-muted-foreground",
        className,
      )}
      {...props}
    />
  );
}

export function TableCell({ className, ...props }: ComponentProps<"td">) {
  return <td className={cn("h-10 px-3 align-middle", className)} {...props} />;
}
