import { AppSidebar } from "@/components/app-sidebar";
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { createRootRoute, Outlet } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";

const RootLayout = () => (
  <>
    <SidebarProvider defaultOpen={true}>
      <AppSidebar variant="inset" />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12">
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger className="-ml-1" />
          </div>
        </header>
        <Outlet />
      </SidebarInset>
    </SidebarProvider>
    <TanStackRouterDevtools position={"bottom-right"} />
  </>
);

const NotFound = () => (
  <div className="flex flex-col justify-center items-center h-full">
    <div>
      <h1 className="inline-block mr-3 pr-3 border-r-1 border-white-300">404</h1>
      <div className="inline-block">
        <h2>This page could not be found.</h2>
      </div>
    </div>
  </div>
)

export const Route = createRootRoute({ component: RootLayout, notFoundComponent: NotFound });
