import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import API from "@/lib/api";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";

export const Route = createFileRoute("/login")({
  component: RouteComponent,
});

function RouteComponent() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isPasswordInvalid, setIsPasswordInvalid] = useState(false);

  const loginMutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) => {
      setIsPasswordInvalid(false);
      return API.auth.login(email, password);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["me"] });
      navigate({ to: "/" });
    },
    onError(error) {
      if (error.message === "Invalid credentials") {
        setIsPasswordInvalid(true);
        setPassword("");
      }
    },
  });

  return (
    <div className="flex flex-1 flex-col min-h-fit w-full items-center justify-center p-6 md:p-10">
      <div className="w-full max-w-sm">
        <div className="flex flex-col gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Login to your account</CardTitle>
              <CardDescription>
                Enter your email below to login to your account.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form>
                <FieldGroup>
                  <Field>
                    <FieldLabel htmlFor="email">Email</FieldLabel>
                    <Input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="m@example.com"
                      required
                    />
                  </Field>
                  <Field data-invalid={isPasswordInvalid}>
                    <FieldLabel htmlFor="password">Password</FieldLabel>

                    <Input
                      aria-invalid={isPasswordInvalid}
                      id="password"
                      type="password"
                      value={password}
                      onChange={(e) => {
                        setPassword(e.target.value);
                        setIsPasswordInvalid(false);
                      }}
                      required
                    />
                    {isPasswordInvalid && (
                      <FieldError>Invalid Password</FieldError>
                    )}
                  </Field>
                  <Field>
                    <Button
                      type="submit"
                      onClick={(e) => {
                        e.preventDefault();
                        loginMutation.mutate({ email, password });
                      }}
                    >
                      Login
                    </Button>
                    {/*<Button
                      variant="outline"
                      type="button"
                      onClick={() =>
                        authClient.signIn.social({
                          provider: "github",
                        })
                      }
                    >
                      Login with Github
                    </Button>*/}
                    <FieldDescription className="text-center">
                      Don&apos;t have an account?{" "}
                      <Link to="/signup">Sign up</Link>
                    </FieldDescription>
                  </Field>
                </FieldGroup>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
