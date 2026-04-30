import { useUser } from "@/hooks/useUser";

export const Show = ({
  children,
  when,
}: {
  children: React.ReactNode;
  when: "signed-in" | "signed-out";
}) => {
  const { isAuthenticated } = useUser();

  if (isAuthenticated && when === "signed-in") {
    return <div>{children}</div>;
  }

  if (!isAuthenticated && when === "signed-out") {
    return <div>{children}</div>;
  }
};
