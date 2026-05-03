import {
  LayoutDashboard, Users, FolderKanban, CalendarCheck,
  Palette, Building2, LogOut, Bell, ChevronRight,
} from "lucide-react";
import { NavLink, useLocation } from "react-router-dom";
import {
  Sidebar, SidebarContent, SidebarFooter, SidebarGroup,
  SidebarGroupContent, SidebarGroupLabel, SidebarHeader,
  SidebarMenu, SidebarMenuButton, SidebarMenuItem, useSidebar,
} from "@/components/ui/sidebar";
import { useAuthStore } from "@/store/authStore";
import { useQuery } from "@tanstack/react-query";
import { notificationsApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const mainNav = [
  { title: "Dashboard", url: "/dashboard", icon: LayoutDashboard },
  { title: "Contractors", url: "/contractors", icon: Users },
  { title: "Projects", url: "/projects", icon: FolderKanban },
  { title: "Bookings", url: "/bookings", icon: CalendarCheck },
  { title: "Designs", url: "/designs", icon: Palette },
];

export function AppSidebar() {
  const { state } = useSidebar();
  const collapsed = state === "collapsed";
  const { pathname } = useLocation();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

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

  const isActive = (url: string) =>
    pathname === url || pathname.startsWith(url + "/");

  const initials = user?.name
    ? user.name.split(" ").map((p) => p[0]).join("").slice(0, 2).toUpperCase()
    : "U";

  return (
    <Sidebar collapsible="icon" className="border-r border-sidebar-border">
      <SidebarHeader className="border-b border-sidebar-border px-0">
        <div className={cn("flex items-center gap-3 px-4 py-4", collapsed && "justify-center px-2")}>
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-accent shadow-md">
            <Building2 className="h-5 w-5 text-white" />
          </div>
          {!collapsed && (
            <div className="flex flex-col leading-tight">
              <span className="text-sm font-bold text-sidebar-foreground tracking-tight">
                BuildHub
              </span>
              <span className="text-[10px] uppercase tracking-widest text-sidebar-foreground/40">
                Construction OS
              </span>
            </div>
          )}
        </div>
      </SidebarHeader>

      <SidebarContent className="py-2">
        <SidebarGroup>
          {!collapsed && (
            <SidebarGroupLabel className="px-4 text-[10px] uppercase tracking-widest text-sidebar-foreground/40">
              Workspace
            </SidebarGroupLabel>
          )}
          <SidebarGroupContent>
            <SidebarMenu className="gap-0.5 px-2">
              {mainNav.map((item) => {
                const active = isActive(item.url);
                return (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton asChild isActive={active}>
                      <NavLink
                        to={item.url}
                        className={cn(
                          "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all",
                          active
                            ? "bg-sidebar-primary text-sidebar-primary-foreground shadow-sm"
                            : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-foreground",
                          collapsed && "justify-center px-2"
                        )}
                      >
                        <item.icon className={cn("h-4 w-4 shrink-0", active && "text-white")} />
                        {!collapsed && (
                          <span className="flex-1">{item.title}</span>
                        )}
                        {!collapsed && item.title === "Bookings" && unreadCount > 0 && (
                          <span className="flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-sidebar-primary-foreground/20 px-1.5 text-[10px] font-bold text-sidebar-primary-foreground">
                            {unreadCount}
                          </span>
                        )}
                        {!collapsed && active && (
                          <ChevronRight className="h-3 w-3 opacity-60" />
                        )}
                      </NavLink>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-sidebar-border">
        {user && (
          <div className={cn("flex items-center gap-3 p-3", collapsed && "justify-center")}>
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-accent text-xs font-bold text-white shadow-sm">
              {initials}
            </div>
            {!collapsed && (
              <>
                <div className="flex min-w-0 flex-1 flex-col">
                  <span className="truncate text-xs font-semibold text-sidebar-foreground">
                    {user.name}
                  </span>
                  <span className="truncate text-[10px] capitalize text-sidebar-foreground/50">
                    {user.role}
                  </span>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={logout}
                  className="h-7 w-7 text-sidebar-foreground/50 hover:bg-sidebar-accent hover:text-sidebar-foreground"
                  aria-label="Sign out"
                >
                  <LogOut className="h-3.5 w-3.5" />
                </Button>
              </>
            )}
          </div>
        )}
      </SidebarFooter>
    </Sidebar>
  );
}
