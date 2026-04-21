import { HouseholdSwitcher } from "@/components/household-switcher";
import { NavUser } from "@/components/nav-user";
import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarHeader,
    SidebarRail,
} from "@/components/ui/sidebar";
import { AudioWaveform, Command, GalleryVerticalEnd } from "lucide-react";

// Testing Data
const data = {
  user: {
    name: "Jpuf",
    email: "jpuf@jpuf.xyz",
    avatar: "https://avatars.githubusercontent.com/u/38541170?v=4"
  },
  households: [
    {
      name: "Test 1",
      logo: GalleryVerticalEnd,
    },
    {
      name: "Test 2",
      logo: AudioWaveform,
    },
    {
      name: "Test 3",
      logo: Command,
    },
  ]
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <HouseholdSwitcher households={data.households} />
      </SidebarHeader>
      <SidebarContent>
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
