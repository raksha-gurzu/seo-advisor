const numberFormat = new Intl.NumberFormat("en");

export function formatCount(value: number): string {
  return numberFormat.format(value);
}

export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export function formatMs(ms: number): string {
  if (ms < 1000) return `${ms} ms`;
  return `${(ms / 1000).toFixed(ms < 10_000 ? 2 : 1)} s`;
}

const relative = new Intl.RelativeTimeFormat("en", { numeric: "auto" });

export function formatRelative(iso: string, now: Date = new Date()): string {
  const seconds = Math.round((new Date(iso).getTime() - now.getTime()) / 1000);
  const abs = Math.abs(seconds);
  if (abs < 60) return relative.format(seconds, "second");
  if (abs < 3600) return relative.format(Math.round(seconds / 60), "minute");
  if (abs < 86_400) return relative.format(Math.round(seconds / 3600), "hour");
  return relative.format(Math.round(seconds / 86_400), "day");
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

/** "https://host" without the scheme: the name we show for a site. */
export function hostOf(url: string): string {
  return new URL(url).host;
}

/** The path and query of a URL, for tables where the host is the same for all rows. */
export function pathOf(url: string): string {
  const parsed = new URL(url);
  return `${parsed.pathname}${parsed.search}`;
}

/** The last path part of a URL, e.g. "sitemap.xml". */
export function fileOf(url: string): string {
  const parts = new URL(url).pathname.split("/").filter(Boolean);
  return parts.at(-1) ?? "/";
}

/** "snake_case" -> "Snake case" for page types. */
export function humanize(value: string): string {
  const text = value.replaceAll("_", " ");
  return text.charAt(0).toUpperCase() + text.slice(1);
}
