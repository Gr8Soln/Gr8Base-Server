import { createFileRoute, Outlet, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Menu } from "lucide-react";
import { Sidebar } from "@/components/caros/Sidebar";
import { CarosMark } from "@/components/caros/CarosMark";
import { useAuth } from "@/lib/auth";
import { Sheet, SheetContent, SheetTrigger, SheetTitle } from "@/components/ui/sheet";

export const Route = createFileRoute("/dashboard")({
  component: DashboardLayout,
});

function DashboardLayout() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => {
      if (!user) navigate({ to: "/auth/login" as any });
    }, 50);
    return () => clearTimeout(t);
  }, [user, navigate]);

  return (
    <div className="min-h-screen flex bg-background">
      <div className="hidden md:flex shrink-0 h-screen sticky top-0">
        <Sidebar collapsed={collapsed} onToggleCollapsed={() => setCollapsed((c) => !c)} />
      </div>

      <main className="flex-1 min-w-0">
        {/* Mobile top bar */}
        <header className="md:hidden sticky top-0 z-30 h-14 flex items-center justify-between border-b border-border bg-background/90 backdrop-blur px-4">
          <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
            <SheetTrigger asChild>
              <button
                aria-label="Open menu"
                className="rounded-md p-2 text-muted-foreground hover:bg-elevated hover:text-foreground transition-colors"
              >
                <Menu className="h-5 w-5" />
              </button>
            </SheetTrigger>
            <SheetContent side="left" className="p-0 w-72 bg-surface border-border">
              <SheetTitle className="sr-only">Navigation</SheetTitle>
              <Sidebar mobile onNavigate={() => setMobileOpen(false)} />
            </SheetContent>
          </Sheet>
          <CarosMark size="sm" />
          <div className="w-9" />
        </header>

        <div className="mx-auto max-w-7xl px-4 sm:px-6 md:px-10 lg:px-12 py-6 md:py-10">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
