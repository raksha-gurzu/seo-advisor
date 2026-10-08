import { useQuery } from "@tanstack/react-query";
import { Link, Outlet, useMatchRoute } from "@tanstack/react-router";
import { Globe, Monitor, Moon, Search, Sun } from "lucide-react";
import type { ReactNode } from "react";

import { CommandPalette, useCommandPalette } from "@/app/command-palette";
import { type ThemeChoice, useTheme } from "@/app/theme";
import { healthQuery, sitesQuery } from "@/features/sites/queries";
import { SiteMark } from "@/features/sites/site-mark";
import { hostOf } from "@/shared/lib/format";
import { cn } from "@/shared/lib/utils";
import { Button } from "@/shared/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuTrigger,
} from "@/shared/ui/dropdown-menu";
import { Kbd } from "@/shared/ui/kbd";
import { TooltipText } from "@/shared/ui/tooltip";

export function AppShell() {
  const palette = useCommandPalette();
  return (
    <div className="flex min-h-svh">
      <aside className="sticky top-0 hidden h-svh w-60 shrink-0 flex-col border-r bg-sidebar md:flex">
        <Brand />
        <div className="px-3">
          <SearchButton onClick={() => palette.setOpen(true)} />
        </div>
        <nav className="mt-5 flex-1 space-y-6 overflow-y-auto px-3" aria-label="Main">
          <NavSection title="Workspace">
            <NavLink link={{ to: "/sites" }} icon={<Globe className="size-4" />} exact>
              Sites
            </NavLink>
          </NavSection>
          <SiteLinks />
        </nav>
        <footer className="flex items-center justify-between border-t px-3 py-2.5">
          <ApiStatus />
          <ThemeMenu />
        </footer>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex h-14 items-center justify-between border-b bg-background/90 px-4 backdrop-blur md:hidden">
          <Link to="/sites" className="flex items-center gap-2 font-semibold">
            <Logo /> seo-advisor
          </Link>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon-sm"
              aria-label="Search"
              onClick={() => palette.setOpen(true)}
            >
              <Search />
            </Button>
            <ThemeMenu />
          </div>
        </header>
        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 md:px-8 md:py-8">
          <Outlet />
        </main>
      </div>
      <CommandPalette open={palette.open} onOpenChange={palette.setOpen} />
    </div>
  );
}

function Logo() {
  return <img src="/favicon.svg" alt="" className="size-6" />;
}

function Brand() {
  return (
    <Link to="/sites" className="flex items-center gap-2.5 px-4 pt-4 pb-4">
      <Logo />
      <span className="leading-tight">
        <span className="block text-sm font-semibold tracking-tight">seo-advisor</span>
        <span className="block text-[11px] text-muted-foreground">SEO platform</span>
      </span>
    </Link>
  );
}

function SearchButton({ onClick }: { onClick: () => void }) {
  const mac = /Mac|iPhone|iPad/.test(navigator.userAgent);
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex h-8 w-full items-center gap-2 rounded-md border bg-card px-2.5 text-[13px] text-muted-foreground shadow-xs transition-colors hover:text-foreground"
    >
      <Search className="size-3.5" />
      <span className="flex-1 text-left">Search…</span>
      <Kbd>{mac ? "⌘" : "Ctrl"}</Kbd>
      <Kbd>K</Kbd>
    </button>
  );
}

function NavSection({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div>
      <p className="mb-1.5 px-2 text-[11px] font-medium tracking-wide text-muted-foreground uppercase">
        {title}
      </p>
      <ul className="space-y-0.5">{children}</ul>
    </div>
  );
}

type NavTarget = { to: "/sites" } | { to: "/sites/$siteId"; params: { siteId: string } };

function NavLink({
  link,
  icon,
  exact = false,
  children,
}: {
  link: NavTarget;
  icon: ReactNode;
  exact?: boolean;
  children: ReactNode;
}) {
  const matchRoute = useMatchRoute();
  const active = Boolean(matchRoute({ ...link, fuzzy: !exact }));
  return (
    <li>
      <Link
        {...link}
        className={cn(
          "flex h-8 items-center gap-2.5 rounded-md px-2 text-[13px] text-muted-foreground transition-colors hover:bg-accent/60 hover:text-foreground",
          active && "bg-accent font-medium text-accent-foreground hover:bg-accent",
        )}
      >
        {icon}
        <span className="truncate">{children}</span>
      </Link>
    </li>
  );
}

function SiteLinks() {
  const sites = useQuery(sitesQuery());
  if (!sites.data || sites.data.length === 0) return null;
  return (
    <NavSection title="Sites">
      {sites.data.map((site) => {
        const host = hostOf(site.base_url);
        return (
          <NavLink
            key={site.id}
            link={{ to: "/sites/$siteId", params: { siteId: site.id } }}
            icon={<SiteMark host={host} className="size-5 rounded text-[10px] shadow-none" />}
          >
            {host}
          </NavLink>
        );
      })}
    </NavSection>
  );
}

function ApiStatus() {
  const health = useQuery(healthQuery());
  const online = health.isSuccess && !health.isError;
  const label = health.isPending ? "Checking API…" : online ? "API online" : "API offline";
  return (
    <TooltipText
      content={online ? "GET /health answers" : "Start it with: make dev"}
      className="flex items-center gap-2 text-xs text-muted-foreground"
    >
      <span
        className={cn(
          "size-2 rounded-full",
          health.isPending ? "bg-muted-foreground/40" : online ? "bg-success" : "bg-critical",
        )}
      />
      {label}
    </TooltipText>
  );
}

const THEME_ICON = { light: Sun, dark: Moon, system: Monitor } as const;

function ThemeMenu() {
  const { choice, setChoice } = useTheme();
  const Icon = THEME_ICON[choice];
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon-sm" aria-label="Theme">
          <Icon />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel>Theme</DropdownMenuLabel>
        <DropdownMenuRadioGroup
          value={choice}
          onValueChange={(value) => setChoice(value as ThemeChoice)}
        >
          <DropdownMenuRadioItem value="light">Light</DropdownMenuRadioItem>
          <DropdownMenuRadioItem value="dark">Dark</DropdownMenuRadioItem>
          <DropdownMenuRadioItem value="system">System</DropdownMenuRadioItem>
        </DropdownMenuRadioGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
