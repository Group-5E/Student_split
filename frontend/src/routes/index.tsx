import { Button } from "@/components/ui/button";
import API from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";

function Index() {
  const hello = useQuery({
    queryKey: ["hello"],
    queryFn: () => API.req("posts/hello", "POST", { text: "from Flask" })
  })
  const session = undefined;

  return (
    <div className="container flex flex-col items-center justify-center gap-12 px-4 py-16">
      <div className="flex flex-col items-center gap-2">
        <p className="text-2xl text-white">
          {hello ? hello.data : "Loading query..."}
        </p>

        <div className="flex flex-col items-center justify-center gap-4">
          <p className="text-center text-2xl text-white">
            {/*{session && <span>Logged in as {session.user?.name}</span>}*/}
          </p>
          {!session ? (
            <Button asChild>
              <a href="/signin">Sign in</a>
            </Button>
          ) : (
            <form>
              <button
                className="rounded-full bg-white/10 px-10 py-3 font-semibold no-underline transition hover:bg-white/20"
              // formAction={async () => {
              //   "use server";
              //   await auth.api.signOut({
              //     headers: await headers(),
              //   });
              //   redirect("/");
              // }}
              >
                Sign out
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}

export const Route = createFileRoute('/')({
  component: Index,
})
