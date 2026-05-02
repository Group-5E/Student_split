import { useUser } from "@/hooks/useUser";

export const Show = ({
  children,
  when,
}: {
  children: React.ReactNode;
  when: "signed-in" | "signed-out";
}) => {
  const { isAuthenticated, isLoading } = useUser();

  if (isLoading) return null;

  if (isAuthenticated && when === "signed-in") {
    return <>{children}</>;
  }

  if (!isAuthenticated && when === "signed-out") {
    return <>{children}</>;
  }
};
