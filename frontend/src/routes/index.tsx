import { useUser } from "@/hooks/useUser";
import { createFileRoute, Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { Show } from '@/components/auth';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { MoonStar } from "lucide-react";

function Index() {
  const { user, isAuthenticated, hasHousehold} = useUser();
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
              <MoonStar className="size-1/3"/>  
            </ QuestionCard>
            <QuestionCard title={`${month} breakdown`}>
              <p>nothing to show...</p>
              <MoonStar className="size-1/3"/> 
            </ QuestionCard >
            <QuestionCard title="you're running out of...">
              <p>nothing to show...</p>
              <MoonStar className="size-1/3"/> 
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
