import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { PagesTable } from "@/features/inventory/pages-table";
import type { DiscoveredPage } from "@/shared/lib/api";
import { TooltipProvider } from "@/shared/ui/tooltip";

const page = (path: string, pageType: string): DiscoveredPage => ({
  url: `https://m.example${path}`,
  page_type: pageType,
  language: "en",
  lastmod: "",
  sitemap: "https://m.example/sitemap.xml",
});
const PAGES = [
  page("/blog/b", "blog_post"),
  page("/blog", "blog_index"),
  page("/blog/a", "blog_post"),
];
const RULES = [{ pattern: "/blog", page_type: "blog_index" }];

function renderTable(pages = PAGES, onQuery = vi.fn()) {
  render(
    <TooltipProvider>
      <PagesTable
        pages={pages}
        total={PAGES.length}
        rules={RULES}
        query=""
        onQuery={onQuery}
        type={undefined}
        onClearType={vi.fn()}
      />
    </TooltipProvider>,
  );
}

const paths = () =>
  screen
    .getAllByRole("row")
    .slice(1)
    .map((row) => within(row).getAllByRole("cell")[0]?.textContent);

describe("PagesTable", () => {
  it("sorts by path, and the header reverses the order", () => {
    renderTable();
    expect(paths()).toEqual(["/blog", "/blog/a", "/blog/b"]);
    fireEvent.click(screen.getByRole("button", { name: /path/i }));
    expect(paths()).toEqual(["/blog/b", "/blog/a", "/blog"]);
  });

  it("reports what the filter shows and sends typed text", () => {
    const onQuery = vi.fn();
    renderTable(PAGES.slice(0, 1), onQuery);
    expect(screen.getByText("1 of 3 pages")).toBeTruthy();
    fireEvent.change(screen.getByLabelText("Filter pages by path"), { target: { value: "a" } });
    expect(onQuery).toHaveBeenCalledWith("a");
  });

  it("says so when no page matches", () => {
    renderTable([]);
    expect(screen.getByText("No page matches this filter.")).toBeTruthy();
  });
});
