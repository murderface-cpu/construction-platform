import { Bell } from "lucide-react";
import { Outlet, Link } from "react-router-dom";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "./AppSidebar";
import { Button } from "@/components/ui/button";
import { useQuery } from "@tanstack/react-query";
import { notificationsApi } from "@/lib/api";
import { useAuthStore } from "@/store/authStore";
import { cn } from "@/lib/utils";

export default function AppLayout() {
  const user = useAuthStore((s) => s.user);

  const { data: unreadCount = 0 } = useQuery({
    queryKey: ["notifications-count"],
    queryFn: async () => {
      try {
        const { data } = await notificationsApi.unreadCount();
        return data?.count ?? data?.unread_count ?? 0;
      } catch { return 0; }
    },
    refetchInterval: 60_000,
  });

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full bg-background">
        <AppSidebar />
        <div className="flex flex-1 flex-col min-w-0">
          <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-border bg-card/90 px-4 backdrop-blur-md">
            <SidebarTrigger className="text-muted-foreground hover:text-foreground" />
            <div className="flex flex-1 items-center justify-end gap-2">
              <Button variant="ghost" size="icon" className="relative" aria-label="Notifications">
                <Bell className="h-4 w-4" />
                {unreadCount > 0 && (
                  <span className="absolute right-1.5 top-1.5 flex h-2 w-2 rounded-full bg-accent" />
                )}
              </Button>
              {user && (
                <div className="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-accent text-[11px] font-bold text-white">
                  {user.name.split(" ").map((p) => p[0]).join("").slice(0, 2).toUpperCase()}
                </div>
              )}
            </div>
          </header>
          <main className="flex-1 animate-fade-in">
            <Outlet />
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}
