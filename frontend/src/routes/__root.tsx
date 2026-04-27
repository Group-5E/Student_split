import { AppSidebar } from "@/components/app-sidebar";
import { ModeToggle } from "@/components/mode-toggle";
import { ThemeProvider } from "@/components/theme-provider";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { TooltipProvider } from "@/components/ui/tooltip";
import { createRootRoute, Outlet } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";

const RootLayout = () => (
  <>
    <ThemeProvider defaultTheme="system" storageKey="theme">
      <SidebarProvider>
        <TooltipProvider>
          <AppSidebar variant="inset" />
          <SidebarInset>
            <header className="sticky top-0 flex h-12 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12 px-4">
              <SidebarTrigger className="-ml-1" />
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

export const Route = createRootRoute({
  component: RootLayout,
  notFoundComponent: NotFound,
});
