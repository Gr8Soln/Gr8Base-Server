import { useState } from "react";
import { Link, useRouterState } from "@tanstack/react-router";
import {
  LayoutDashboard, FileText, Briefcase, BarChart3, Wand2, UserCircle2, LogOut,
  ChevronLeft, ChevronRight,
} from "lucide-react";
import { CarosMark } from "./CarosMark";
import { useAuth } from "@/lib/auth";
import { cn } from "@/lib/utils";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

type Item = { to: string; label: string; icon: typeof LayoutDashboard; exact?: boolean };
const items: Item[] = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard, exact: true },
  { to: "/dashboard/resumes", label: "Resumes", icon: FileText },
  { to: "/dashboard/jobs", label: "Jobs", icon: Briefcase },
  { to: "/dashboard/ats", label: "ATS Scores", icon: BarChart3 },
  { to: "/dashboard/optimize", label: "Optimize", icon: Wand2 },
  { to: "/dashboard/profile", label: "Profile", icon: UserCircle2 },
];

type SidebarProps = {
  collapsed?: boolean;
  onToggleCollapsed?: () => void;
  /** When true, render full-width inside a mobile sheet (no toggle button, always expanded). */
  mobile?: boolean;
  onNavigate?: () => void;
};

export function Sidebar({ collapsed = false, onToggleCollapsed, mobile = false, onNavigate }: SidebarProps) {
  const { user, signOut } = useAuth();
  const path = useRouterState({ select: (s) => s.location.pathname });
  const [confirmOpen, setConfirmOpen] = useState(false);

  const isCollapsed = !mobile && collapsed;

  return (
    <TooltipProvider delayDuration={100}>
      <aside
        className={cn(
          "relative h-screen shrink-0 flex flex-col border-r border-border bg-surface transition-[width] duration-200",
          mobile ? "w-full" : isCollapsed ? "w-16" : "md:w-60 lg:w-64",
        )}
      >
        <div
          className={cn(
            "h-16 border-b border-border flex items-center",
            isCollapsed ? "justify-center px-2" : "px-6 justify-between",
          )}
        >
          {isCollapsed ? (
            <span className="font-bold text-lg tracking-tight">
              <span className="text-emerald">C</span>
            </span>
          ) : (
            <CarosMark size="md" />
          )}
          {!mobile && (
            <button
              onClick={onToggleCollapsed}
              className={cn(
                "rounded-md p-1.5 text-muted-foreground hover:bg-elevated hover:text-foreground transition-colors",
                isCollapsed && "absolute -right-3 top-5 z-10 bg-surface border border-border h-6 w-6 flex items-center justify-center p-0 rounded-full",
              )}
              title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            >
              {isCollapsed ? <ChevronRight className="h-3.5 w-3.5" /> : <ChevronLeft className="h-4 w-4" />}
            </button>
          )}
        </div>

        <nav className={cn("flex-1 py-4 space-y-0.5 overflow-y-auto", isCollapsed ? "px-2" : "px-3")}>
          {items.map((it) => {
            const active = it.exact ? path === it.to : path === it.to || path.startsWith(it.to + "/");
            const Icon = it.icon;
            const link = (
              <Link
                key={it.to}
                to={it.to as any}
                onClick={onNavigate}
                className={cn(
                  "relative flex items-center gap-3 rounded-lg text-sm transition-all duration-200",
                  isCollapsed ? "justify-center px-2 py-2.5" : "px-3 py-2",
                  active
                    ? "bg-elevated text-emerald font-medium"
                    : "text-muted-foreground hover:bg-elevated hover:text-foreground",
                )}
              >
                {active && !isCollapsed && (
                  <span className="absolute left-0 top-1.5 bottom-1.5 w-0.5 rounded-r bg-emerald" />
                )}
                <Icon className="h-4 w-4 shrink-0" />
                {!isCollapsed && <span>{it.label}</span>}
              </Link>
            );
            if (isCollapsed) {
              return (
                <Tooltip key={it.to}>
                  <TooltipTrigger asChild>{link}</TooltipTrigger>
                  <TooltipContent side="right">{it.label}</TooltipContent>
                </Tooltip>
              );
            }
            return link;
          })}
        </nav>

        <div className={cn("border-t border-border", isCollapsed ? "p-2" : "p-3")}>
          <div className={cn("flex items-center rounded-lg", isCollapsed ? "flex-col gap-2 py-2" : "gap-3 px-3 py-2")}>
            {user?.avatarUrl && (
              <img src={user.avatarUrl} alt="" className="h-8 w-8 rounded-full bg-elevated shrink-0" />
            )}
            {!isCollapsed && (
              <div className="min-w-0 flex-1">
                <div className="text-sm font-medium text-foreground truncate">{user?.name}</div>
                <div className="text-xs text-muted-foreground truncate">{user?.email}</div>
              </div>
            )}
            {isCollapsed ? (
              <Tooltip>
                <TooltipTrigger asChild>
                  <button
                    onClick={() => setConfirmOpen(true)}
                    className="rounded-md p-1.5 text-muted-foreground hover:bg-elevated hover:text-foreground transition-colors"
                  >
                    <LogOut className="h-4 w-4" />
                  </button>
                </TooltipTrigger>
                <TooltipContent side="right">Sign out</TooltipContent>
              </Tooltip>
            ) : (
              <button
                onClick={() => setConfirmOpen(true)}
                title="Sign out"
                className="rounded-md p-1.5 text-muted-foreground hover:bg-elevated hover:text-foreground transition-colors"
              >
                <LogOut className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      </aside>

      <Dialog open={confirmOpen} onOpenChange={setConfirmOpen}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle>Sign out?</DialogTitle>
            <DialogDescription>
              Are you sure you want to sign out of CAROS?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="sm:justify-end gap-2">
            <Button variant="ghost" onClick={() => setConfirmOpen(false)}>
              Cancel
            </Button>
            <Button
              className="bg-emerald hover:bg-emerald-hover text-emerald-foreground"
              onClick={() => {
                setConfirmOpen(false);
                signOut();
              }}
            >
              Sign out
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </TooltipProvider>
  );
}
