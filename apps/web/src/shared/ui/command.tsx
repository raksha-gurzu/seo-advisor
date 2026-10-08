import { Command as Cmdk } from "cmdk";
import { Dialog } from "radix-ui";
import { Search } from "lucide-react";
import type { ComponentProps, ReactNode } from "react";

import { cn } from "@/shared/lib/utils";

/** The command palette window (cmdk inside a Radix dialog). */
export function CommandDialog({
  open,
  onOpenChange,
  children,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: ReactNode;
}) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 animate-in bg-black/30 backdrop-blur-[2px] fade-in-0" />
        <Dialog.Content className="fixed top-[18%] left-1/2 z-50 w-[calc(100%-2rem)] max-w-xl -translate-x-1/2 animate-in overflow-hidden rounded-xl border bg-popover text-popover-foreground shadow-2xl fade-in-0 zoom-in-95">
          <Dialog.Title className="sr-only">Command palette</Dialog.Title>
          <Dialog.Description className="sr-only">
            Search for a page or an action.
          </Dialog.Description>
          <Cmdk loop className="flex flex-col">
            {children}
          </Cmdk>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

export function CommandInput(props: ComponentProps<typeof Cmdk.Input>) {
  return (
    <div className="flex items-center gap-2 border-b px-4">
      <Search className="size-4 text-muted-foreground" aria-hidden />
      <Cmdk.Input
        className="h-12 w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
        {...props}
      />
    </div>
  );
}

export function CommandList({ className, ...props }: ComponentProps<typeof Cmdk.List>) {
  return <Cmdk.List className={cn("max-h-80 overflow-y-auto p-2", className)} {...props} />;
}

export function CommandEmpty(props: ComponentProps<typeof Cmdk.Empty>) {
  return <Cmdk.Empty className="py-8 text-center text-sm text-muted-foreground" {...props} />;
}

export function CommandGroup({ className, ...props }: ComponentProps<typeof Cmdk.Group>) {
  return (
    <Cmdk.Group
      className={cn(
        "[&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-1.5 [&_[cmdk-group-heading]]:text-xs [&_[cmdk-group-heading]]:font-medium [&_[cmdk-group-heading]]:text-muted-foreground",
        className,
      )}
      {...props}
    />
  );
}

export function CommandItem({ className, ...props }: ComponentProps<typeof Cmdk.Item>) {
  return (
    <Cmdk.Item
      className={cn(
        "flex cursor-default items-center gap-2.5 rounded-md px-2 py-2 text-sm outline-none select-none data-[selected=true]:bg-accent data-[selected=true]:text-accent-foreground [&_svg]:size-4 [&_svg]:text-muted-foreground",
        className,
      )}
      {...props}
    />
  );
}
