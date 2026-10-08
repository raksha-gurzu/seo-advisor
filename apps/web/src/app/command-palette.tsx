import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { Activity, Globe, ListTree, Monitor, Moon, Play, Shapes, Sun } from "lucide-react";
import { useEffect, useState } from "react";

import { useTheme } from "@/app/theme";
import { useRunDiscovery } from "@/features/inventory/queries";
import { sitesQuery } from "@/features/sites/queries";
import { hostOf } from "@/shared/lib/format";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/shared/ui/command";

/** Ctrl+K / Cmd+K: go to any screen or start an action from the keyboard. */
export function useCommandPalette() {
  const [open, setOpen] = useState(false);
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key.toLowerCase() === "k" && (event.metaKey || event.ctrlKey)) {
        event.preventDefault();
        setOpen((value) => !value);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);
  return { open, setOpen };
}

export function CommandPalette({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const navigate = useNavigate();
  const sites = useQuery(sitesQuery());
  const run = useRunDiscovery();
  const { setChoice } = useTheme();

  const close = (action: () => void) => () => {
    onOpenChange(false);
    action();
  };

  return (
    <CommandDialog open={open} onOpenChange={onOpenChange}>
      <CommandInput placeholder="Search screens and actions…" />
      <CommandList>
        <CommandEmpty>No match.</CommandEmpty>
        <CommandGroup heading="Go to">
          <CommandItem onSelect={close(() => void navigate({ to: "/sites" }))}>
            <Globe /> Sites
          </CommandItem>
          {sites.data?.map((site) => {
            const host = hostOf(site.base_url);
            const params = { siteId: site.id };
            return [
              <CommandItem
                key={`${site.id}-inventory`}
                value={`${host} inventory pages`}
                onSelect={close(() => void navigate({ to: "/sites/$siteId", params }))}
              >
                <ListTree /> {host} <span className="text-muted-foreground">· Inventory</span>
              </CommandItem>,
              <CommandItem
                key={`${site.id}-rules`}
                value={`${host} rules page types test url`}
                onSelect={close(() => void navigate({ to: "/sites/$siteId/rules", params }))}
              >
                <Shapes /> {host} <span className="text-muted-foreground">· Rules</span>
              </CommandItem>,
              <CommandItem
                key={`${site.id}-activity`}
                value={`${host} activity requests trace`}
                onSelect={close(() => void navigate({ to: "/sites/$siteId/activity", params }))}
              >
                <Activity /> {host} <span className="text-muted-foreground">· Activity</span>
              </CommandItem>,
            ];
          })}
        </CommandGroup>
        <CommandGroup heading="Actions">
          {sites.data?.map((site) => (
            <CommandItem
              key={`${site.id}-run`}
              value={`run discovery ${hostOf(site.base_url)}`}
              onSelect={close(() => run.mutate(site.id))}
            >
              <Play /> Run discovery on {hostOf(site.base_url)}
            </CommandItem>
          ))}
        </CommandGroup>
        <CommandGroup heading="Theme">
          <CommandItem onSelect={close(() => setChoice("light"))}>
            <Sun /> Light
          </CommandItem>
          <CommandItem onSelect={close(() => setChoice("dark"))}>
            <Moon /> Dark
          </CommandItem>
          <CommandItem onSelect={close(() => setChoice("system"))}>
            <Monitor /> Same as the system
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}
