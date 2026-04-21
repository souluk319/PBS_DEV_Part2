import type { ReactNode } from "react";

import {
  Bot,
  Boxes,
  BookOpen,
  BriefcaseBusiness,
  Cable,
  GitBranch,
  Home,
  LayoutDashboard,
  PlaySquare,
  SlidersHorizontal,
  ServerCog,
} from "lucide-react";

import { Button } from "@/shared/ui/button";
import { cn } from "@/shared/lib/cn";
import type { AppRoute } from "@/app/routes";

type SidebarProps = {
  open: boolean;
  activeRoute: AppRoute;
  onNavigate: (route: AppRoute) => void;
  onClose: () => void;
  railContent?: ReactNode;
  footerContent?: ReactNode;
};

const navItems: Array<{
  route: AppRoute;
  label: string;
  icon: typeof Cable;
}> = [
  { route: "workspaces", label: "Workspaces", icon: BriefcaseBusiness },
  { route: "connections", label: "Connections", icon: Cable },
  { route: "models", label: "Models", icon: SlidersHorizontal },
  { route: "overview", label: "Overview", icon: LayoutDashboard },
  { route: "resources", label: "Resources", icon: ServerCog },
  { route: "library", label: "Library", icon: Boxes },
  { route: "chat", label: "Chat", icon: Bot },
  { route: "actions", label: "Actions", icon: PlaySquare },
  { route: "scm", label: "SCM", icon: GitBranch },
];

const DEFAULT_SHELL_BASE_URL = "http://127.0.0.1:5173";

function resolveShellBaseUrl(): string {
  const envBaseUrl = String(import.meta.env.VITE_PUBLIC_SHELL_BASE_URL ?? "").trim().replace(/\/$/, "");
  if (envBaseUrl) {
    return envBaseUrl;
  }
  if (typeof window !== "undefined" && window.top !== window) {
    const referrer = String(document.referrer || "").trim();
    if (referrer) {
      try {
        return new URL(referrer).origin;
      } catch {
        return DEFAULT_SHELL_BASE_URL;
      }
    }
  }
  return DEFAULT_SHELL_BASE_URL;
}

export function Sidebar({
  open,
  activeRoute,
  onNavigate,
  onClose,
  railContent,
  footerContent,
}: SidebarProps) {
  const shellBaseUrl = resolveShellBaseUrl();
  const exitLinks = [
    { href: `${shellBaseUrl}/studio`, label: "Studio", icon: BookOpen },
    { href: `${shellBaseUrl}/`, label: "Home", icon: Home },
  ];

  return (
    <>
      <div
        className={cn(
          "fixed inset-0 z-40 bg-black/60 transition-opacity lg:hidden",
          open ? "opacity-100" : "pointer-events-none opacity-0",
        )}
        onClick={onClose}
      />
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-72 flex-col border-r border-border bg-[#0d0e12] px-4 py-5 transition-transform lg:static lg:z-auto lg:w-64 lg:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="mb-6 flex items-center justify-between lg:justify-start">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.22em] text-primary">
              OCP Console
            </div>
            <div className="mt-2 font-display text-2xl font-semibold tracking-tight text-foreground">
              OCPOps
            </div>
          </div>
          <Button variant="ghost" size="sm" className="lg:hidden" onClick={onClose}>
            Close
          </Button>
        </div>

        <nav className="grid gap-1">
          {navItems.map(({ route, label, icon: Icon }) => {
            const active = activeRoute === route;
            return (
              <button
                key={route}
                type="button"
                onClick={() => {
                  onNavigate(route);
                  onClose();
                }}
                className={cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-medium transition-colors",
                  active
                    ? "bg-[#15181e] text-foreground shadow-[inset_4px_0_0_0_rgba(16,96,255,1)]"
                    : "text-muted-foreground hover:bg-[#15181e] hover:text-foreground",
                )}
              >
                <Icon className="h-5 w-5" />
                <span>{label}</span>
              </button>
            );
          })}
        </nav>

        {railContent ? <div className="mt-6 overflow-auto pr-1">{railContent}</div> : null}

        <div className="mt-auto pt-4">
          {footerContent ? <div>{footerContent}</div> : null}
          <div className={cn("grid gap-1", footerContent ? "mt-4 border-t border-border/70 pt-4" : "")}>
            {exitLinks.map(({ href, label, icon: Icon }) => (
              <a
                key={label}
                href={href}
                target="_top"
                rel="noreferrer"
                onClick={onClose}
                className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-medium text-muted-foreground transition-colors hover:bg-[#15181e] hover:text-foreground"
              >
                <Icon className="h-5 w-5" />
                <span>{label}</span>
              </a>
            ))}
          </div>
        </div>
      </aside>
    </>
  );
}
