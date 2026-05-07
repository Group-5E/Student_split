import { useUser } from "@/hooks/useUser";
import { createFileRoute, Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { Show } from '@/components/auth';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { MoonStar } from "lucide-react";
import { ChartContainer, ChartTooltip, ChartTooltipContent, type ChartConfig } from "@/components/ui/chart";
import { LabelList, Pie, PieChart } from "recharts";

const chartData = [
  { browser: "chrome", visitors: 275, fill: "var(--color-chrome)" },
  { browser: "safari", visitors: 200, fill: "var(--color-safari)" },
  { browser: "firefox", visitors: 187, fill: "var(--color-firefox)" },
  { browser: "edge", visitors: 173, fill: "var(--color-edge)" },
  { browser: "other", visitors: 90, fill: "var(--color-other)" },
]
const chartConfig = {
  visitors: {
    label: "Visitors",
  },
  chrome: {
    label: "Chrome",
    color: "var(--chart-1)",
  },
  safari: {
    label: "Safari",
    color: "var(--chart-2)",
  },
  firefox: {
    label: "Firefox",
    color: "var(--chart-3)",
  },
  edge: {
    label: "Edge",
    color: "var(--chart-4)",
  },
  other: {
    label: "Other",
    color: "var(--chart-5)",
  },
} satisfies ChartConfig

function Index() {
  const { user, isAuthenticated, hasHousehold } = useUser();
  const date = new Date();
  const month = date.toLocaleString('default', { month: 'long' })

  return (
    <div className="w-full h-full flex flex-col items-center justify-center gap-12 px-4 py-16">
      <Show when="signed-out">
        <Card className="w-64 max-w-sm">
          <CardHeader>
            <CardTitle className="justify-center items-center flex flex-col">
              welcome to student split
            </CardTitle>
          </CardHeader>
          <CardFooter className="flex-col gap-2">
            <Button className="w-full" asChild>
              <Link to="/login">Login</Link>
            </Button>
            <Button className="w-full" asChild>
              <Link to="/signup">Sign Up</Link>
            </Button>
          </CardFooter>
        </Card>
      </Show>
      <Show when="signed-in">
        <Card className="flex w-full h-full flex-row gap-5 px-5 py-5 items-center justify-around *:flex *:w-full *:h-full">
          <Show when="homeless">
            <QuestionCard title="Next Payment">
              <p>nothing to show...</p>
              <MoonStar className="size-1/4" />
            </ QuestionCard>
            <QuestionCard title={`${month} breakdown`}>
              <p>nothing to show...</p>
              <MoonStar className="size-1/4" />
            </ QuestionCard >
            <QuestionCard title="you're running out of...">
              <p>nothing to show...</p>
              <MoonStar className="size-1/4" />
            </ QuestionCard>
          </Show>
        </Card>
      </Show>
      <div className="flex flex-col items-center justify-center gap-4">
        <Card className="flex p-3">
          <p className="text-center text-2xl dark:text-white">
            {user && <span>Logged in as {user?.username}</span>}
          </p>
        </Card>
      </div>
    </div>
  );
}
function QuestionCard({ title, children }: { title: string; children?: React.ReactNode }) {
  return (
    <Card className="flex w-full h-full justify-center items-center">
      <CardTitle className="flex items-center justify-center w-full h-1/10 text-2xl">
        {title}
      </CardTitle>
      <CardContent className="flex flex-col w-full h-full items-center justify-center gap-5">{children}</CardContent>
    </Card>
  );
}

export const Route = createFileRoute("/")({
  component: Index,
});
