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
      body: body ? JSON.stringify(body) : undefined
    });

    const result = await req.json();
    return result;
  }
}
