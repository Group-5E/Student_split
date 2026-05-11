import { Button } from "@/components/ui/button";
import { Card, CardContent, CardTitle } from "@/components/ui/card";
import {
  Combobox,
  ComboboxContent,
  ComboboxEmpty,
  ComboboxInput,
  ComboboxItem,
  ComboboxList,
} from "@/components/ui/combobox";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import {
  Item,
  ItemContent,
  ItemDescription,
  ItemTitle,
} from "@/components/ui/item";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { useUser } from "@/hooks/useUser";
import API from "@/lib/api";
import {
  ExpenseResponse,
  type Expense,
  type Household,
  type HouseholdMember,
  type Split,
  type SplitType,
} from "@/lib/types";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { toast } from "sonner";

export const Route = createFileRoute("/admin")({
  component: RouteComponent,
});

function RouteComponent() {
  const addUserMutation = useMutation({
    mutationFn: ({
      username,
      name,
      email,
      password,
    }: {
      username: string;
      name: string;
      email: string;
      password: string;
    }) => API.auth.register(username, name, email, password),
    onSuccess: () => {
      toast.success("User added successfully");
    },
    onError: (error) => {
      toast.error("Failed to add user", { description: error.message });
    },
  });

  const addUserToHousehold = useMutation({
    mutationFn: ({
      username,
      householdId,
    }: {
      username: string;
      householdId: string;
    }) =>
      API.req(`households/${householdId}/members/add`, "POST", { username }),
    onSuccess: () => {
      toast.success("User added to household successfully");
    },
    onError: (error) => {
      toast.error("Failed to add user to household", {
        description: error.message,
      });
    },
  });

  const addTenUsers = () => {
    for (let i = 0; i < 10; i++) {
      addUserMutation.mutate({
        username: `user${i}`,
        name: `User ${i}`,
        email: `user${i}@example.com`,
        password: `password${i}`,
      });
    }
  };

  const migrateUsers = () => {
    for (let i = 0; i < 10; i++) {
      addUserToHousehold.mutate({
        username: `user${i}`,
        householdId: "1",
      });
    }
  };

  //@ts-expect-error process does not exist...
  if (process.env.NODE_ENV !== "development") {
    return null;
  }

  return (
    <div className="w-full h-full flex flex-col items-center justify-center gap-4 p-4">
      <Card className="flex w-full h-full gap-4">
        <CardTitle className="flex items-center justify-center">
          Admin Backend Functions
        </CardTitle>
        <CardContent className="flex flex-col gap-4">
          {/*<Button onClick={migrateUsers}>Add User</Button>*/}
          <HouseholdCard />
          <ExpenseCard />
        </CardContent>
      </Card>
    </div>
  );
}

function HouseholdCard() {
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");
  const queryClient = useQueryClient();

  const createHousehold = useMutation({
    mutationFn: () => API.req("households/create", "POST", { name, address }),
    onSuccess: () => {
      toast.success("Household created successfully");
      queryClient.invalidateQueries({ queryKey: ["households"] });
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const householdsQuery = useQuery({
    queryKey: ["households"],
    queryFn: () => API.req<Household[]>("households/list", "GET"),
  });

  return (
    <Card>
      <CardTitle className="flex items-center justify-center">
        Household
      </CardTitle>
      <CardContent className="flex flex-row gap-4 w-full h-full">
        <Card className="w-full h-full">
          <CardTitle className="flex items-center justify-center">
            Create
          </CardTitle>
          <CardContent>
            <form className="pb-2">
              <Field>
                <FieldLabel htmlFor="household-name">Name</FieldLabel>
                <Input
                  id="household-name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="household-address">Address</FieldLabel>
                <Input
                  id="household-address"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                />
              </Field>
            </form>
            <Button
              onClick={(e) => {
                e.preventDefault();
                createHousehold.mutate();
              }}
            >
              Submit
            </Button>
          </CardContent>
        </Card>
        <Card className="w-full h-full">
          <CardTitle className="flex items-center justify-center">
            List Households
          </CardTitle>
          <CardContent>
            <ScrollArea className="h-42">
              {householdsQuery.data && (
                <div className="flex w-full flex-col gap-2 text-sm pr-4">
                  {householdsQuery.data.map((household) => (
                    <>
                      <dl className="flex items-center justify-between">
                        <dt key={household.id}>{household.name}</dt>
                        <dd>
                          <Button variant={"destructive"}>Delete</Button>
                        </dd>
                      </dl>
                      <Separator />
                    </>
                  ))}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      </CardContent>
    </Card>
  );
}

function ExpenseCard() {
  const { user } = useUser();

  const [description, setDescription] = useState("");
  const [splits, setSplits] = useState<Split[]>([]);

  const expensesQuery = useQuery({
    queryKey: ["expense"],
    queryFn: () =>
      API.req<ExpenseResponse[]>(
        `expenses/list?household_id=${user?.household_id}`,
        "GET",
      ),
  });

  const createExpenseMutation = useMutation({
    mutationFn: (expense: Expense) =>
      API.req(`expenses/create`, "POST", { ...expense }),
  });

  return (
    <Card>
      <CardTitle className="flex items-center justify-center">
        Expenses
      </CardTitle>
      <CardContent className="flex flex-row gap-4 w-full h-full">
        <Card className="w-full h-full">
          <CardTitle className="flex items-center justify-center">
            Create
          </CardTitle>
          <CardContent>
            <form className="pb-2">
              <FieldGroup>
                <Field>
                  <FieldLabel htmlFor="expense-description">
                    Description
                  </FieldLabel>
                  <Input
                    id="expense-description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                  />
                </Field>
                {/*<Field>
                  <FieldLabel htmlFor="expense-amount">Amount</FieldLabel>
                  <Input
                    id="expense-amount"
                    value={amount}
                    type="number"
                    onChange={(e) => setAmount(parseInt(e.target.value))}
                  />
                </Field>*/}
                <ExpenseDialog setSplits={setSplits} splits={splits} />
              </FieldGroup>
            </form>
            <Button
              onClick={(e) => {
                e.preventDefault();
                const amount = splits.reduce(
                  (acc, split) => acc + split.amount,
                  0,
                );

                createExpenseMutation.mutate({
                  amount,
                  description,
                  expense_date: new Date(),
                  household_id: 1,
                  splits,
                });
              }}
            >
              Submit
            </Button>
          </CardContent>
        </Card>

        <Card className="w-full h-full">
          <CardTitle className="flex items-center justify-center">
            List Expences
          </CardTitle>
          <CardContent>
            <ScrollArea className="h-42">
              {expensesQuery.data && (
                <div className="flex w-full flex-col gap-2 text-sm pr-4">
                  {expensesQuery.data.map((expense) => (
                    <>
                      <Item>
                        <ItemContent>
                          <ItemTitle>{expense.description}</ItemTitle>
                          <ItemDescription>{expense.amount}</ItemDescription>
                        </ItemContent>
                      </Item>
                      <Separator />
                    </>
                  ))}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      </CardContent>
    </Card>
  );
}

function ExpenseDialog({
  splits,
  setSplits,
}: {
  splits: Split[];
  setSplits: React.Dispatch<React.SetStateAction<Split[]>>;
}) {
  const [comboValue, setComboValue] = useState<HouseholdMember | null>(null);
  const [amount, setAmount] = useState<number>(0);
  const [splitType, setSplitType] = useState<SplitType>("equal");

  const household = 1;

  const householdMembers = useQuery({
    queryKey: ["household-members"],
    queryFn: () =>
      API.req<HouseholdMember[]>(`households/${household}/members/list`, "GET"),
  });

  const handleSubmit = () => {
    const split: Split = {
      amount,
      split_type: splitType,
      name: comboValue?.name ?? "",
      user_id: comboValue?.user_id ?? 0,
    };

    setSplits([...splits, split]);
  };

  return (
    <>
      <Field>
        <FieldLabel>Expense Splits</FieldLabel>
        <Card>
          <CardContent className="flex flex-col gap-2">
            {splits.map((split) => (
              <Item variant={"outline"} key={split.user_id}>
                <ItemContent>
                  <ItemTitle>{split.name}</ItemTitle>
                  <ItemDescription>{`${split.split_type} - ${split.amount}`}</ItemDescription>
                </ItemContent>
              </Item>
            ))}
          </CardContent>
        </Card>
      </Field>
      <Dialog>
        <DialogTrigger asChild>
          <Button>Add Split</Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Split</DialogTitle>
          </DialogHeader>
          <FieldGroup>
            <Field>
              <FieldLabel>Member</FieldLabel>
              <Combobox
                value={comboValue}
                onValueChange={setComboValue}
                items={householdMembers.data}
                itemToStringLabel={(member) => member.name}
              >
                <ComboboxInput placeholder="Select a member" />
                <ComboboxContent className="pointer-events-auto">
                  <ComboboxEmpty>No members found</ComboboxEmpty>
                  <ComboboxList>
                    {(member) => (
                      <ComboboxItem key={member.user_id} value={member}>
                        {member.name}
                      </ComboboxItem>
                    )}
                  </ComboboxList>
                </ComboboxContent>
              </Combobox>
            </Field>
            <Field>
              <FieldLabel>Amount</FieldLabel>
              <Input
                type="number"
                placeholder="Enter amount"
                value={amount}
                onChange={(e) => setAmount(Number(e.target.value))}
              />
            </Field>
            <Field>
              <FieldLabel>Split Type</FieldLabel>
              <Select
                value={splitType}
                onValueChange={(value) => setSplitType(value as SplitType)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select split type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectItem value="equal">Equal</SelectItem>
                    <SelectItem value="percentage">Percentage</SelectItem>
                    <SelectItem value="fixed">Fixed</SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
            </Field>
          </FieldGroup>
          <Button onClick={handleSubmit}>Submit</Button>
        </DialogContent>
      </Dialog>
    </>
  );
}
