import { useUser } from "@/hooks/useUser";
import API from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";

function Index() {
  const { user } = useUser();

  const hello = useQuery({
    queryKey: ["hello"],
    queryFn: () => API.req("posts/hello", "POST", { text: "from Flask" }),
  });

  return (
    <div className="w-full flex flex-col items-center justify-center gap-12 px-4 py-16">
      <div className="flex flex-col items-center gap-2">
        <p className="text-2xl dark:text-white">
          {hello ? hello.data : "Loading query..."}
        </p>

        <div className="flex flex-col items-center justify-center gap-4">
          <p className="text-center text-2xl dark:text-white">
            {user && <span>Logged in as {user?.name}</span>}
          </p>
        </div>
      </div>
    </div>
  );
}

export const Route = createFileRoute("/")({
  component: Index,
});
