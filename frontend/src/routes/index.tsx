import { Show } from "@/components/auth";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Field, FieldGroup } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import {
  Item,
  ItemContent,
  ItemDescription,
  ItemTitle,
} from "@/components/ui/item";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableFooter,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useUser } from "@/hooks/useUser";
import API from "@/lib/api";
import type {
  ExpenseResponse,
  HouseholdMember,
  UpcomingPayment,
} from "@/lib/types";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createFileRoute, Link } from "@tanstack/react-router";
import { MoonStar } from "lucide-react";
import { useState } from "react";

const getUpcomingExpenses = (
  expenses: ExpenseResponse[],
  currentUserId: number,
): UpcomingPayment[] => {
  return expenses
    .filter((e) => e.paid_by_id !== currentUserId)
    .flatMap((e) => {
      const mySplit = e.splits.find(
        (s) => s.user_id === currentUserId && !s.is_settled,
      );
      if (!mySplit) return [];
      return [
        {
          splitId: mySplit.id,
          expenseId: e.id,
          description: e.description,
          category: e.category,
          amount: parseFloat(mySplit.amount_owed),
          owedTo: e.paid_by_name,
          owedToId: e.paid_by_id,
          expenseDate: new Date(e.expense_date),
        },
      ];
    })
    .sort((a, b) => a.expenseDate.getTime() - b.expenseDate.getTime());
};

function Index() {
  const { user } = useUser();
  const date = new Date();
  const month = date.toLocaleString("default", { month: "long" });

  const { data: expenses } = useQuery({
    queryKey: ["household-expenses"],
    queryFn: () =>
      API.req<ExpenseResponse[]>(
        `expenses/list?household_id=${user?.household_id}`,
      ),
    enabled: !!user?.household_id,
  });

  const { data: members } = useQuery({
    queryKey: ["household-members"],
    queryFn: () =>
      API.req<HouseholdMember[]>(
        `households/${user?.household_id}/members/list`,
      ),
    enabled: !!user?.household_id,
  });

  const upcoming = expenses ? getUpcomingExpenses(expenses, user!.id) : [];

  return (
    <div className="w-full h-full flex flex-col items-center justify-center gap-12 px-4 py-4">
      <Show when="signed-out">
        <Card className="w-64 max-w-sm">
          <CardHeader>
            <CardTitle className="justify-center items-center flex flex-col">
              welcome to student split
            </CardTitle>
          </CardHeader>
          <CardFooter className="flex-col gap-2">
            <Button className="w-full" asChild>
              <Link to="/login">Login</Link>
            </Button>
            <Button className="w-full" asChild>
              <Link to="/signup">Sign Up</Link>
            </Button>
          </CardFooter>
        </Card>
      </Show>
      <Show when="signed-in">
        <Show when="homeless">
          <CreateHouseholdDialog />
        </Show>
        <Show when="housed">
          <Card className="flex w-full h-full flex-row gap-5 px-5 py-5 items-center justify-around">
            <QuestionCard title="Next Payment">
              {expenses ? (
                <>
                  {upcoming.map((expense) => (
                    <Item variant={"outline"} key={expense.expenseId}>
                      <ItemContent>
                        <ItemTitle>{expense.description}</ItemTitle>
                        <ItemDescription>{`£${expense.amount} to ${expense.owedTo} due on ${expense.expenseDate.toLocaleDateString()}`}</ItemDescription>
                      </ItemContent>
                    </Item>
                  ))}
                </>
              ) : (
                <>
                  <p>nothing to show...</p>
                  <MoonStar className="size-1/4" />
                </>
              )}
            </QuestionCard>
            <QuestionCard title={`${month} breakdown`}>
              {expenses ? (
                <MonthBreakdown expenses={expenses} />
              ) : (
                <>
                  <p>nothing to show...</p>
                  <MoonStar className="size-1/4" />
                </>
              )}
            </QuestionCard>
            <QuestionCard title="People in your household">
              {members ? (
                <div className="flex flex-col overflow-y-scroll w-full gap-2">
                  {members
                    .sort((a, b) => a.user_id - b.user_id)
                    .map((member) => (
                      <Item variant={"outline"} key={member.user_id}>
                        <ItemContent>
                          <ItemTitle>{member.name}</ItemTitle>
                          <ItemDescription>{member.username}</ItemDescription>
                        </ItemContent>
                      </Item>
                    ))}
                </div>
              ) : (
                <>
                  <p>nothing to show...</p>
                  <MoonStar className="size-1/4" />
                </>
              )}
            </QuestionCard>
          </Card>
        </Show>
        <div className="flex flex-col items-center justify-center gap-4">
          <Card className="flex p-3">
            <p className="text-center text-2xl dark:text-white">
              {user && <span>Logged in as {user?.username}</span>}
            </p>
          </Card>
        </div>
      </Show>
    </div>
  );
}

function QuestionCard({
  title,
  children,
}: {
  title: string;
  children?: React.ReactNode;
}) {
  return (
    <Card className="flex w-full h-full justify-center items-center">
      <CardTitle className="flex items-center justify-center w-full h-1/10 text-2xl">
        {title}
      </CardTitle>
      <CardContent className="flex flex-col w-full h-full items-center justify-center gap-5">
        {children}
      </CardContent>
    </Card>
  );
}

function MonthBreakdown({ expenses }: { expenses: ExpenseResponse[] }) {
  return (
    <>
      <Table>
        <TableCaption>Month Breakdown</TableCaption>
        <TableHeader>
          <TableRow>
            <TableCell>Expense</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Category</TableCell>
            <TableCell>Amount</TableCell>
          </TableRow>
        </TableHeader>
        <TableBody>
          {expenses
            .sort((a, b) => a.id - b.id)
            .map((expense) => (
              <TableRow key={expense.id}>
                <TableCell>{expense.id}</TableCell>
                <TableCell>
                  {expense.splits.every((split) => split.is_settled)
                    ? "Settled"
                    : "Pending"}
                </TableCell>
                <TableCell>{expense.category}</TableCell>
                <TableCell>{expense.amount}</TableCell>
              </TableRow>
            ))}
        </TableBody>
        <TableFooter>
          <TableRow>
            <TableCell colSpan={3}>Total </TableCell>
            <TableCell>
              {expenses.reduce(
                (acc, expense) => acc + parseFloat(expense.amount),
                0,
              )}
            </TableCell>
          </TableRow>
        </TableFooter>
      </Table>
    </>
  );
}

function CreateHouseholdDialog() {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");

  const queryClient = useQueryClient();

  const createHousehold = useMutation({
    mutationFn: async () => {
      API.req("households/create", "POST", { name, address });
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["households"] }),
        queryClient.invalidateQueries({ queryKey: ["me"] }),
      ]);
      setOpen(false);
    },
  });

  return (
    <Card className="flex lg:w-1/3 sm:w-2/3 gap-4 px-4">
      <CardHeader className="flex flex-col items-center justify-center">
        <CardTitle>Create a Household</CardTitle>
        <CardDescription>
          You don't seem to be in a household yet.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col items-center justify-center">
        <Dialog open={open} onOpenChange={setOpen}>
          <form>
            <DialogTrigger asChild>
              <Button>Create a new household</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create a Household</DialogTitle>
              </DialogHeader>
              <FieldGroup>
                <Field>
                  <Label htmlFor="household-name">Name</Label>
                  <Input
                    id="household-name"
                    name="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                  />
                </Field>
                <Field>
                  <Label htmlFor="household-address">Address</Label>
                  <Input
                    id="household-address"
                    name="address"
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                  />
                </Field>
              </FieldGroup>
              <DialogFooter>
                <DialogClose>
                  <Button variant="outline">Cancel</Button>
                </DialogClose>
                <Button
                  type="submit"
                  onClick={() => {
                    createHousehold.mutate();
                  }}
                >
                  Save changes
                </Button>
              </DialogFooter>
            </DialogContent>
          </form>
        </Dialog>
      </CardContent>
    </Card>
  );
}

export const Route = createFileRoute("/")({
  component: Index,
});
