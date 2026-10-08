import { describe, expect, it } from "vitest";

import { pageTypeColor, pageTypeOrder } from "@/features/inventory/page-types";

const rules = [
  { pattern: "/blog", page_type: "blog_index" },
  { pattern: "/blog/*", page_type: "blog_post" },
  { pattern: "/b/*", page_type: "blog_post" },
];

describe("page types", () => {
  it("gives each type a stable colour in rule order, and grey to other", () => {
    expect(pageTypeColor(rules, "blog_index")).toBe("var(--cat-1)");
    expect(pageTypeColor(rules, "blog_post")).toBe("var(--cat-2)");
    expect(pageTypeColor(rules, "other")).toBe("var(--cat-other)");
  });

  it("orders types by the rules, then the types that only the run found", () => {
    expect(pageTypeOrder(rules, ["other", "blog_post"])).toEqual([
      "blog_index",
      "blog_post",
      "other",
    ]);
  });
});
