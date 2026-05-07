import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardTitle } from "@/components/ui/card";
import { FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { useUser } from "@/hooks/useUser";
import API from "@/lib/api";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { UserRound } from "lucide-react";
import { useEffect, useState } from "react";

export const Route = createFileRoute("/account")({
  component: RouteComponent,
});

function RouteComponent() {
  const { user, isLoading } = useUser();

  const queryClient = useQueryClient();

  const [useremail, setUserEmail] = useState(user?.email ?? "");
  const [username, setUserName] = useState(user?.username ?? "");
  const [userfname, setUserFName] = useState(user?.name ?? "");
  const [edit, setEdit] = useState(true);

  // Update state when user data loads
  useEffect(() => {
    if (user) {
      setUserEmail(user.email ?? "");
      setUserName(user.username ?? "");
      setUserFName(user.name ?? "");
    }
  }, [user]);

  const editUser = useMutation({
    mutationFn: async () => {
      API.req("auth/update", "PUT", {
        username: username,
        name: userfname,
        email: useremail,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["me"] });
      setEdit(true);
    },
  });

  const opacity1 = edit ? 50 : 100;

  if (isLoading || !user) {
    return (
      <div className="w-full h-full flex justify-center items-center p-5">
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="w-full h-full flex flex-wrap justify-center gap-2 p-5">
      <Card className="flex lg:w-[40%] sm:w-full gap-20">
        <CardTitle>
          <Avatar className="mx-auto size-50">
            <AvatarImage src={user?.avatar} alt={user?.username} />
            <AvatarFallback className="round-lg">
              {user ? (
                user.username?.charAt(0)
              ) : (
                <UserRound className="size-50" />
              )}
            </AvatarFallback>
          </Avatar>
        </CardTitle>
        <CardContent className="h-full p-5">
          <form className="h-full flex flex-col gap-2 justify-around">
            <div>
              <FieldLabel htmlFor="username" className="py-2">
                username
              </FieldLabel>
              <Input
                className={`opacity-${opacity1}`}
                id="username"
                type="username"
                value={username}
                readOnly={edit}
                onChange={(e) => setUserName(e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="email" className="py-2">
                email
              </FieldLabel>
              <Input
                className={`opacity-${opacity1}`}
                id="email"
                type="email"
                value={useremail}
                readOnly={edit}
                onChange={(e) => setUserEmail(e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="name" className="py-2">
                name
              </FieldLabel>
              <Input
                className={`opacity-${opacity1}`}
                id="name"
                type="name"
                value={userfname}
                readOnly={edit}
                onChange={(e) => setUserFName(e.target.value)}
              />
            </div>
          </form>
        </CardContent>
        <CardFooter className="flex flex-row-reverse h-max-[20px]">
          {edit ? (
            <Button
              variant="outline"
              type="button"
              onClick={(e) => {
                e.preventDefault();
                setEdit(!edit);
              }}
            >
              edit
            </Button>
          ) : (
            <Button
              variant="default"
              type="button"
              onClick={(e) => {
                e.preventDefault();
                editUser.mutate();
              }}
            >
              save
            </Button>
          )}
        </CardFooter>
      </Card>
    </div>
  );
}
