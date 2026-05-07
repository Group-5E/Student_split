import type { User } from "@/lib/types";

export default class API {
  static req = async <T = any>(
    endpoint: string,
    method: "GET" | "POST" | "PUT" | "DELETE" = "GET",
    body?: Record<string, unknown>,
  ): Promise<T> => {
    const response = await fetch(`/api/${endpoint}`, {
      method,
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    const result: unknown = await response.json();

    if (!response.ok) {
      const error =
        (result as { error?: string }).error || "An unknown error occurred";
      throw new Error(error);
    }

    return result as T;
  };

  static auth = {
    me: () => API.req<{ user: User }>("auth/me"),
    register: (
      username: string,
      name: string,
      email: string,
      password: string,
    ) => API.req("auth/register", "POST", { username, name, email, password }),
    login: (email: string, password: string) =>
      API.req("auth/login", "POST", { email, password }),
    logout: () => API.req("auth/logout", "POST"),
    // github: () => (window.location.href = "/api/auth/github"),
  };
}
