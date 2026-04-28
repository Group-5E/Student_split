import { HouseholdSwitcher } from "@/components/household-switcher";
import { NavUser } from "@/components/nav-user";
import { Button } from "@/components/ui/button";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar";
import { useUser } from "@/hooks/useUser";
import { Link } from "@tanstack/react-router";
import { House } from "lucide-react";
import { NavMain } from "./nav-main";

// Testing Data
const data = {
  user: {
    name: "Jpuf",
    email: "jpuf@jpuf.xyz",
    avatar: "https://avatars.githubusercontent.com/u/38541170?v=4",
  },
  households: [
    {
      name: "Test 1",
      logo: House,
    },
    {
      name: "Test 2",
      logo: House,
    },
    {
      name: "Test 3",
      logo: House,
    },
  ],
};

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const { user } = useUser();

  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <HouseholdSwitcher households={data.households} />
      </SidebarHeader>
      <SidebarContent>
        <NavMain />
      </SidebarContent>
      <SidebarFooter>
      <NavUser user={user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
