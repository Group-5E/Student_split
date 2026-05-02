import { AppSidebar } from "@/components/app-sidebar";
import { Show } from "@/components/auth";
import { ModeToggle } from "@/components/mode-toggle";
import { ThemeProvider } from "@/components/theme-provider";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Spinner } from "@/components/ui/spinner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { meQueryOptions } from "@/hooks/useUser";
import type { QueryClient } from "@tanstack/react-query";
import { createRootRouteWithContext, Outlet } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";

const RootLayout = () => (
  <>
    <ThemeProvider defaultTheme="system" storageKey="theme">
      <SidebarProvider>
        <TooltipProvider>
          <Show when="signed-in">
            <AppSidebar variant="inset" />
          </Show>
          <SidebarInset>
            <header className="sticky top-0 flex h-12 z-1000 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12 px-4">
              <Show when="signed-in">
                <SidebarTrigger className="-ml-1" />
              </Show>
              <div className="ml-auto">
                <ModeToggle />
              </div>
            </header>
            <Outlet />
          </SidebarInset>
        </TooltipProvider>
      </SidebarProvider>
    </ThemeProvider>
    <TanStackRouterDevtools position={"bottom-right"} />
  </>
);

const NotFound = () => (
  <div className="flex flex-col justify-center items-center h-full">
    <div>
      <h1 className="inline-block mr-3 pr-3 border-r border-white-300">404</h1>
      <div className="inline-block">
        <h2>This page could not be found.</h2>
      </div>
    </div>
  </div>
);

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()(
  {
    component: RootLayout,
    notFoundComponent: NotFound,
    pendingComponent: () => <Spinner />,
    beforeLoad: async ({ context: { queryClient } }) => {
      await queryClient.ensureQueryData(meQueryOptions);
    },
  },
);
