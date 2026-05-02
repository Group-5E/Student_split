import { useUser } from "@/hooks/useUser";
import { createFileRoute, Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { Show } from '@/components/auth';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

function Index() {
  const { user } = useUser();
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
          <Card>
            <CardTitle className="flex items-center justify-center">
              Next Payment
            </CardTitle>
            <CardContent>
            </CardContent>
          </Card>
          <Card>
            <CardTitle className="flex items-center justify-center">
              {month + " Breakdown"}
            </CardTitle>
          </Card>
          <Card>
            <CardTitle className="flex items-center justify-center">
              You're Running Out Of...
            </CardTitle>
          </Card>

        </Card>
      </Show>
      <div className="flex flex-col items-center justify-center gap-4">
        <p className="text-center text-2xl dark:text-white">
          {user && <span>Logged in as {user?.username}</span>}
        </p>
      </div>
    </div>
  );
}

export const Route = createFileRoute("/")({
  component: Index,
});
