import { Button } from "@/components/ui/button";
import { useUser } from "@/hooks/useUser";
import API from "@/lib/api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createFileRoute, Link } from "@tanstack/react-router";

function Index() {
  const queryClient = useQueryClient();
  const { user } = useUser();

  const logoutMutation = useMutation({
    mutationFn: () => API.auth.logout(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["me"] });
    },
  });

  const hello = useQuery({
    queryKey: ["hello"],
    queryFn: () => API.req("posts/hello", "POST", { text: "from Flask" }),
  });

  return (
    <div className="container flex flex-col items-center justify-center gap-12 px-4 py-16">
      <div className="flex flex-col items-center gap-2">
        <p className="text-2xl text-white">
          {hello ? hello.data : "Loading query..."}
        </p>

        <div className="flex flex-col items-center justify-center gap-4">
          <p className="text-center text-2xl text-white">
            {user && <span>Logged in as {user?.name}</span>}
          </p>
          {!user ? (
            <Button size={"lg"} asChild>
              <Link to="/login">Sign in</Link>
            </Button>
          ) : (
            <form>
              <Button
                size={"lg"}
                onClick={(e) => {
                  e.preventDefault();
                  logoutMutation.mutate();
                }}
              >
                Sign out
              </Button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

export const Route = createFileRoute("/")({
  component: Index,
});
