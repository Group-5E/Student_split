export default class API {
  static req = async (
    endpoint: string,
    method: "GET" | "POST" = "GET",
    body?: Record<string, unknown>,
  ) => {
    const req = await fetch(`/api/${endpoint}`, {
      method,
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!req.ok) {
      const result = await req.json();
      throw new Error(result.error);
    } else {
      const result = await req.json();
      return result;
    }
  };

  static auth = {
    me: () => API.req("auth/me"),
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
