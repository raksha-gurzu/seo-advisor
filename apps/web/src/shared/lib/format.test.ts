import { describe, expect, it } from "vitest";

import { fileOf, formatBytes, formatMs, humanize, pathOf } from "@/shared/lib/format";

describe("format", () => {
  it("shows sizes in B, KB and MB", () => {
    expect(formatBytes(512)).toBe("512 B");
    expect(formatBytes(12_025)).toBe("11.7 KB");
    expect(formatBytes(50 * 1024 * 1024)).toBe("50.0 MB");
  });

  it("shows times in ms below one second", () => {
    expect(formatMs(840)).toBe("840 ms");
    expect(formatMs(2310)).toBe("2.31 s");
  });

  it("splits URLs into path and file", () => {
    expect(pathOf("https://m.example/blog/a?x=1")).toBe("/blog/a?x=1");
    expect(fileOf("https://m.example/sitemaps/pages.xml")).toBe("pages.xml");
    expect(fileOf("https://m.example/")).toBe("/");
  });

  it("makes page types readable", () => {
    expect(humanize("blog_post")).toBe("Blog post");
  });
});
