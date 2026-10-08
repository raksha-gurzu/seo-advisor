import { pageTypeColor } from "@/features/inventory/page-types";
import type { PageTypeRule } from "@/shared/lib/api";
import { formatCount, humanize } from "@/shared/lib/format";
import { cn } from "@/shared/lib/utils";
import { Tooltip } from "@/shared/ui/tooltip";

export type TypeCount = { type: string; count: number };

/** A stacked bar of page types; the chips below it also filter the pages table. */
export function TypeDistribution({
  counts,
  total,
  rules,
  selected,
  onSelect,
}: {
  counts: TypeCount[];
  total: number;
  rules: PageTypeRule[];
  selected: string | undefined;
  onSelect: (type: string | undefined) => void;
}) {
  return (
    <div>
      <div className="flex h-2.5 w-full gap-0.5 overflow-hidden rounded-full" aria-hidden>
        {counts
          .filter((item) => item.count > 0)
          .map((item) => (
            <Tooltip key={item.type} content={`${humanize(item.type)}: ${item.count}`}>
              <span
                className={cn(
                  "h-full transition-opacity first:rounded-l-full last:rounded-r-full",
                  selected && selected !== item.type && "opacity-25",
                )}
                style={{
                  width: `${(item.count / total) * 100}%`,
                  background: pageTypeColor(rules, item.type),
                }}
              />
            </Tooltip>
          ))}
      </div>
      <div className="mt-3 flex flex-wrap gap-1.5">
        <Chip active={selected === undefined} onClick={() => onSelect(undefined)}>
          All <Count>{formatCount(total)}</Count>
        </Chip>
        {counts.map((item) => (
          <Chip
            key={item.type}
            active={selected === item.type}
            onClick={() => onSelect(selected === item.type ? undefined : item.type)}
            disabled={item.count === 0}
          >
            <span
              className="size-2 rounded-full"
              style={{ background: pageTypeColor(rules, item.type) }}
            />
            {humanize(item.type)} <Count>{formatCount(item.count)}</Count>
          </Chip>
        ))}
      </div>
    </div>
  );
}

function Chip({
  active,
  disabled = false,
  onClick,
  children,
}: {
  active: boolean;
  disabled?: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      aria-pressed={active}
      disabled={disabled}
      onClick={onClick}
      className={cn(
        "inline-flex h-7 items-center gap-1.5 rounded-full border px-2.5 text-xs font-medium transition-colors disabled:opacity-40",
        active
          ? "border-primary/40 bg-accent text-accent-foreground"
          : "bg-card text-foreground hover:bg-muted",
      )}
    >
      {children}
    </button>
  );
}

function Count({ children }: { children: React.ReactNode }) {
  return <span className="text-muted-foreground tabular-nums">{children}</span>;
}
