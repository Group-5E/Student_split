import API from "@/lib/api";
import { queryOptions, useQuery } from "@tanstack/react-query";

export const meQueryOptions = queryOptions({
  queryKey: ["me"],
  queryFn: () => API.auth.me(),
  retry: false,
  staleTime: Infinity,
});

export function useUser() {
  const { data, isLoading } = useQuery(meQueryOptions);
  return {
    user: data?.user ?? null,
    isLoading,
    isAuthenticated: !!data?.user,
  };
}
