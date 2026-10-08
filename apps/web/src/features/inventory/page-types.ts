import type { PageTypeRule } from "@/shared/lib/api";

const CATEGORY_COUNT = 8;

/** A stable colour per page type: the rule order of the site, then "other". */
export function pageTypeColor(rules: PageTypeRule[], pageType: string): string {
  const types = [...new Set(rules.map((rule) => rule.page_type))];
  const index = types.indexOf(pageType);
  if (index === -1) return "var(--cat-other)";
  return `var(--cat-${(index % CATEGORY_COUNT) + 1})`;
}

/** Page types in rule order, then any other type that the run found. */
export function pageTypeOrder(rules: PageTypeRule[], found: Iterable<string>): string[] {
  const order = [...new Set(rules.map((rule) => rule.page_type))];
  for (const type of found) if (!order.includes(type)) order.push(type);
  return order;
}
