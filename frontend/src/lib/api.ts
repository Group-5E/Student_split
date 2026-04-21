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

    const result = await req.json();
    return result;
  };

  static auth = {
    me: () => API.req("auth/me"),
    register: (username: string, email: string, password: string) =>
      API.req("auth/register", "POST", { name: username, email, password }),
    login: (email: string, password: string) =>
      API.req("auth/login", "POST", { email, password }),
    logout: () => API.req("auth/logout", "POST"),
    // github: () => (window.location.href = "/api/auth/github"),
  };
}
