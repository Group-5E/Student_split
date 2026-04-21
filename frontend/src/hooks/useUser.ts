import API from "@/lib/api";
import { useQuery } from "@tanstack/react-query";

export function useUser() {
  const { data, isLoading } = useQuery({
    queryKey: ["me"],
    queryFn: () => API.auth.me(),
    retry: false,
    staleTime: Infinity,
  });

  return {
    user: data?.user ?? null,
    isLoading,
    isAuthenticated: !!data?.user,
  };
}
