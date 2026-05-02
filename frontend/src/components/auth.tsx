import { useUser } from "@/hooks/useUser";

export const Show = ({
  children,
  when,
}: {
  children: React.ReactNode;
  when: "signed-in" | "signed-out" | "housed" | "homeless";
}) => {
  const { isAuthenticated, isLoading, hasHousehold} = useUser();

  if (isLoading) return null;

  switch (when) {
    case "signed-in":
      if (!isAuthenticated) return null;
      return <>{children}</>;
    case "signed-out":
      if (isAuthenticated) return null;
      return <>{children}</>;
    case "housed":
      if (!hasHousehold) return null;
      return <>{children}</>;
    case "homeless":
      if (hasHousehold) return null;
      return <>{children}</>;
  }
};