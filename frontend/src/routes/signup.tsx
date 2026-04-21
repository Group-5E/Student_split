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
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import API from "@/lib/api";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";

export const Route = createFileRoute("/signup")({
  component: SignupPage,
});

export default function SignupPage() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  // const [confirmPassword, setConfirmPassword] = useState("");

  const signupMutation = useMutation({
    mutationFn: ({
      username,
      email,
      password,
    }: {
      username: string;
      email: string;
      password: string;
    }) => API.auth.register(username, email, password),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["me"] });
      navigate({ to: "/" });
    },
  });

  return (
    <div className="flex flex-1 flex-col min-h-fit w-full items-center justify-center p-6 md:p-10">
      <div className="w-full max-w-sm">
        <Card>
          <CardHeader>
            <CardTitle>Create an account</CardTitle>
            <CardDescription>
              Enter your details below to create an account.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form>
              <FieldGroup>
                <Field>
                  <FieldLabel htmlFor="username">Username</FieldLabel>
                  <Input
                    id="username"
                    type="text"
                    placeholder="BigJohn69"
                    onChange={(e) => setUsername(e.target.value)}
                    value={username}
                    autoComplete="off"
                    required
                  />
                </Field>
                <Field>
                  <FieldLabel htmlFor="email">Email</FieldLabel>
                  <Input
                    id="email"
                    type="email"
                    onChange={(e) => setEmail(e.target.value)}
                    value={email}
                    placeholder="m@example.com"
                    autoComplete="off"
                    required
                  />
                </Field>
                <Field>
                  <FieldLabel htmlFor="password">Password</FieldLabel>
                  <Input
                    id="password"
                    type="password"
                    placeholder="BigBoss12!"
                    onChange={(e) => setPassword(e.target.value)}
                    value={password}
                    autoComplete="off"
                    required
                  />
                </Field>
                {/*<Field>
                  <FieldLabel htmlFor="confirm-password">
                    Confirm Password
                  </FieldLabel>
                  <Input
                    id="confirm-password"
                    type="password"
                    placeholder="BigBoss12!"
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    value={confirmPassword}
                    autoComplete="off"
                    required
                  />
                  <FieldDescription>
                    Please confirm your password.
                  </FieldDescription>
                </Field>*/}
                <FieldGroup>
                  <Field>
                    <Button
                      type="submit"
                      onClick={(e) => {
                        e.preventDefault();
                        signupMutation.mutate({ username, email, password });
                      }}
                    >
                      Create Account
                    </Button>
                    {/*<Button
                      variant="outline"
                      type="button"
                      onClick={() =>
                        authClient.signIn.social({ provider: "github" })
                      }
                    >
                      Sign up with Github
                    </Button>*/}
                    <FieldDescription className="px-6 text-center">
                      Already have an account? <Link to="/login">Login</Link>
                    </FieldDescription>
                  </Field>
                </FieldGroup>
              </FieldGroup>
              {/*here we would call a DBS check!!!*/}
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
