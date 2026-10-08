import { cn } from "@/shared/lib/utils";

/** A small square with the site's first letter: a stable mark without fetching a favicon. */
export function SiteMark({ host, className }: { host: string; className?: string }) {
  const name = host.replace(/^www\./, "");
  const letter = name.split(".").find((part) => part.length > 3) ?? name;
  return (
    <span
      aria-hidden
      className={cn(
        "inline-flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary text-sm font-semibold text-primary-foreground uppercase shadow-xs shadow-primary/30",
        className,
      )}
    >
      {letter.charAt(0)}
    </span>
  );
}
