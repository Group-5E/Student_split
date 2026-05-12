import { Button } from "@/components/ui/button";
import { ButtonGroup } from "@/components/ui/button-group";
import {
  Card,
  CardAction,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
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
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import {
  Item,
  ItemActions,
  ItemContent,
  ItemDescription,
  ItemTitle,
} from "@/components/ui/item";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useUser } from "@/hooks/useUser";
import API from "@/lib/api";
import type {
  Expense,
  ExpenseResponse,
  HouseholdMember,
  Split,
  SplitType,
  UpcomingPayment,
} from "@/lib/types";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { Trash } from "lucide-react";
import { Fragment, useState } from "react";

export const Route = createFileRoute("/pay_split")({
  component: RouteComponent,
});

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

function RouteComponent() {
  const { user } = useUser();
  const queryClient = useQueryClient();

  const [selectedExpense, setExpense] = useState<number | undefined>();

  const { data: expenses } = useQuery({
    queryKey: ["household-expenses"],
    queryFn: () =>
      API.req<ExpenseResponse[]>(
        `expenses/list?household_id=${user?.household_id}`,
      ),
    enabled: !!user?.household_id,
  });

  const { data: expense_data } = useQuery({
    queryKey: ["expense-data", selectedExpense],
    queryFn: () => API.req<ExpenseResponse>(`expenses/get/${selectedExpense}`),
    enabled: selectedExpense !== undefined,
  });

  const settleExpense = useMutation({
    mutationFn: ({ split_id }: { split_id: number }) =>
      API.req<void>(`expenses/splits/settle/${split_id}`, "POST", {}),
    onSuccess: (data) => {
      console.log("Expense settled successfully", data);
      Promise.all([
        queryClient.invalidateQueries({ queryKey: ["household-expenses"] }),
        queryClient.invalidateQueries({
          queryKey: ["expense-data", selectedExpense],
        }),
      ]);
    },
    onError: (error) => {
      console.error("Failed to settle expense", error);
    },
  });

  const upcoming = expenses ? getUpcomingExpenses(expenses, user!.id) : [];

  return (
    <div className="h-full w-full p-4">
      <Card className="flex h-full w-full">
        <CardHeader>
          <CardTitle>Pay Expenses</CardTitle>
          <CardAction>
            <CreateExpenseDialog />
          </CardAction>
        </CardHeader>
        {expenses && expenses.length > 0 ? (
          <CardContent className="flex flex-row w-full h-full gap-4">
            <div className="flex flex-col gap-2 h-full w-1/3">
              <>
                {upcoming.map((expense) => (
                  <Item variant={"muted"} key={expense.expenseId}>
                    <ItemContent>
                      <ItemTitle>{expense.description}</ItemTitle>
                      <ItemDescription>{`£${expense.amount} to ${expense.owedTo} due on ${expense.expenseDate.toLocaleDateString()}`}</ItemDescription>
                    </ItemContent>
                    <ItemActions>
                      <Button
                        variant={
                          selectedExpense === expense.expenseId
                            ? "secondary"
                            : "default"
                        }
                        disabled={selectedExpense === expense.expenseId}
                        onClick={() => {
                          setExpense(expense.expenseId);
                        }}
                      >
                        Select
                      </Button>
                    </ItemActions>
                  </Item>
                ))}
              </>
            </div>
            <div className="flex flex-row justify-center items-start w-2/3">
              {selectedExpense && expense_data ? (
                <Card className="w-full">
                  <CardTitle className="flex flex-row items-center justify-center">
                    Payment Details
                  </CardTitle>
                  <CardContent className="flex flex-col gap-2">
                    <div className="flex flex-col gap-4">
                      <Card>
                        <CardTitle className="flex flex-row items-center justify-center">
                          Expense Details
                        </CardTitle>
                        <CardContent className="flex flex-col gap-2">
                          <p>
                            <strong>Description:</strong>{" "}
                            {expense_data.description}
                          </p>
                          <p>
                            <strong>Category:</strong> {expense_data.category}
                          </p>
                          <p>
                            <strong>Amount:</strong> £{expense_data.amount}
                          </p>
                          <p>
                            <strong>Paid By:</strong>{" "}
                            {expense_data.paid_by_name}
                          </p>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardTitle className="flex flex-row items-center justify-center">
                          Splits
                        </CardTitle>
                        <CardContent className="flex flex-col gap-2">
                          <div className="flex flex-col gap-2 items-center justify-center">
                            {expense_data.splits.map((split) => (
                              <Item variant={"outline"} key={split.id}>
                                <ItemContent>
                                  <p>
                                    <strong>Split Owner:</strong>{" "}
                                    {split.username}
                                  </p>
                                  <p>
                                    <strong>Amount:</strong> £
                                    {split.amount_owed}
                                  </p>
                                  <p>
                                    <strong>Is Outstanding:</strong>{" "}
                                    {split.is_settled ? "No" : "Yes"}
                                  </p>
                                </ItemContent>
                                <ItemActions>
                                  <Button
                                    variant={"default"}
                                    disabled={split.is_settled}
                                    onClick={() =>
                                      settleExpense.mutate({
                                        split_id: split.id,
                                      })
                                    }
                                  >
                                    Pay
                                  </Button>
                                </ItemActions>
                              </Item>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <p>No Split selected...</p>
              )}
            </div>
          </CardContent>
        ) : (
          <CardContent className="flex flex-col items-center justify-center h-full">
            <p>No expenses to show.</p>
          </CardContent>
        )}
      </Card>
    </div>
  );
}

function CreateExpenseDialog() {
  const { user } = useUser();
  const queryClient = useQueryClient();

  const [splits, setSplits] = useState<Split[]>([]);
  const [splitType, setSplitType] = useState<SplitType>("equal");
  const [amount, setAmount] = useState<number>(0);
  const [category, setCategory] = useState<string>("Other");
  const [description, setDescription] = useState<string>("");
  const [errors, setErrors] = useState<{
    description?: string;
    category?: string;
    amount?: string;
    splits?: string;
  }>({});

  const updateSplit = (id: number, changes: Partial<Split>) => {
    setSplits((prev) =>
      prev.map((s) => (s.id === id ? { ...s, ...changes } : s)),
    );
    // Clear error if a user is being selected
    if (
      changes.user_id !== undefined &&
      changes.user_id !== -1 &&
      errors.splits
    ) {
      setErrors((prev) => ({ ...prev, splits: undefined }));
    }
  };

  const updateSplitsAmount = (amount: number) => {
    setSplits((prev) =>
      prev.map((s) => ({
        ...s,
        amount: parseInt((amount / prev.length).toFixed(2)),
      })),
    );
  };

  const deleteSplit = (id: number) => {
    setSplits((prev) => prev.filter((s) => s.id !== id));
    updateSplitsAmount(amount);
  };

  const createSplit = () => {
    const lastSplitId = splits.length > 0 ? splits[splits.length - 1].id : 0;
    const splitAmount = amount / (splits.length + 1);

    const split: Split = {
      id: lastSplitId + 1,
      name: "No User Selected",
      amount: splitAmount,
      user_id: -1,
      split_type: splitType,
    };

    setSplits([...splits, split]);
    updateSplitsAmount(amount);
    if (errors.splits) {
      setErrors((prev) => ({ ...prev, splits: undefined }));
    }
  };

  const createExpenseMutation = useMutation({
    mutationFn: (expense: Expense) =>
      API.req("expenses/create", "POST", { ...expense }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["household-expenses"] });
    },
  });

  const validateForm = () => {
    const newErrors: typeof errors = {};

    if (!description.trim()) {
      newErrors.description = "Description is required";
    }

    if (!category.trim()) {
      newErrors.category = "Category is required";
    }

    if (amount <= 0) {
      newErrors.amount = "Amount must be greater than 0";
    }

    if (splits.length === 0) {
      newErrors.splits = "At least one split is required";
    } else if (splits.some((s) => s.user_id === -1)) {
      newErrors.splits = "All splits must have a user selected";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const createExpense = () => {
    if (!validateForm()) return;

    createExpenseMutation.mutate({
      description,
      category,
      amount,
      expense_date: new Date(),
      household_id: user!.household_id!,
      splits,
    });
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Create New Expense</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create Expense</DialogTitle>
        </DialogHeader>
        <FieldGroup>
          <Field data-invalid={errors.description ? "true" : "false"}>
            <FieldLabel>Description</FieldLabel>
            <Input
              type="text"
              value={description}
              aria-invalid={errors.description ? "true" : "false"}
              onChange={(e) => {
                setDescription(e.target.value);
                if (errors.description) {
                  setErrors((prev) => ({ ...prev, description: undefined }));
                }
              }}
            />
            <FieldError>{errors.description}</FieldError>
          </Field>
          <Field data-invalid={errors.category ? "true" : "false"}>
            <FieldLabel>Category</FieldLabel>
            <Input
              type="text"
              value={category}
              aria-invalid={errors.category ? "true" : "false"}
              onChange={(e) => {
                setCategory(e.target.value);
                if (errors.category) {
                  setErrors((prev) => ({ ...prev, category: undefined }));
                }
              }}
            />
            <FieldError>{errors.category}</FieldError>
          </Field>
          <div className="grid grid-cols-2 gap-4">
            <Field data-invalid={errors.amount ? "true" : "false"}>
              <FieldLabel>Amount</FieldLabel>
              <Input
                type="number"
                value={amount}
                aria-invalid={errors.amount ? "true" : "false"}
                onChange={(e) => {
                  setAmount(Number(e.target.value));
                  updateSplitsAmount(Number(e.target.value));
                  if (errors.amount) {
                    setErrors((prev) => ({ ...prev, amount: undefined }));
                  }
                }}
              />
              <FieldError>{errors.amount}</FieldError>
            </Field>
            <Field>
              <FieldLabel>Split Type</FieldLabel>
              <Select
                value={splitType}
                onValueChange={(value) => {
                  const newType = value as SplitType;
                  setSplitType(newType);
                  setSplits((prev) =>
                    prev.map((s) => ({ ...s, split_type: newType })),
                  );
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a split type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="equal">Equal</SelectItem>
                  <SelectItem value="fixed">Fixed</SelectItem>
                  <SelectItem value="percentage">Percentage</SelectItem>
                </SelectContent>
              </Select>
            </Field>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Splits</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 gap-2">
              {splits.map((split) => (
                <Fragment key={split.id}>
                  <Item variant={"muted"}>
                    <ItemContent>
                      <ItemTitle>{split.name}</ItemTitle>
                      <ItemDescription>
                        Amount: {split.amount.toFixed(2)}
                      </ItemDescription>
                    </ItemContent>
                    <ItemActions>
                      <ButtonGroup>
                        <EditSplitPopover
                          split={split}
                          onUpdate={updateSplit}
                        />
                        <Button
                          variant="destructive"
                          onClick={() => deleteSplit(split.id)}
                        >
                          <Trash />
                        </Button>
                      </ButtonGroup>
                    </ItemActions>
                  </Item>
                </Fragment>
              ))}
            </CardContent>
            <CardFooter>
              {/*<CreateSplitPopover />*/}
              <Button className="w-full" onClick={createSplit}>
                Add Split
              </Button>
            </CardFooter>
          </Card>
          {errors.splits && <FieldError>{errors.splits}</FieldError>}
        </FieldGroup>

        <DialogFooter>
          <Button onClick={createExpense}>Create</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function _CreateSplitPopover() {
  const { user } = useUser();

  const { data: members } = useQuery({
    queryKey: ["household-members"],
    queryFn: () =>
      API.req<HouseholdMember[]>(
        `households/${user?.household_id}/members/list`,
      ),
    enabled: !!user?.household_id,
  });

  const [selectedMember, setSelectedMember] = useState<HouseholdMember | null>(
    null,
  );

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button className="w-full">Add Split</Button>
      </PopoverTrigger>
      <PopoverContent>
        <FieldGroup className="gap-4">
          <Field orientation="horizontal">
            <FieldLabel className="w-1/3">Member</FieldLabel>
            <Combobox
              value={selectedMember}
              onValueChange={setSelectedMember}
              items={members}
              itemToStringLabel={(member) => member!.name}
            >
              <ComboboxInput
                className="col-span-2"
                placeholder="Search members..."
              />
              <ComboboxContent className="pointer-events-auto">
                <ComboboxEmpty>No members found.</ComboboxEmpty>
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
        </FieldGroup>
      </PopoverContent>
    </Popover>
  );
}

function EditSplitPopover({
  split,
  onUpdate,
}: {
  split: Split;
  onUpdate: (id: number, changes: Partial<Split>) => void;
}) {
  const { user } = useUser();

  const { data: members } = useQuery({
    queryKey: ["household-members"],
    queryFn: () =>
      API.req<HouseholdMember[]>(
        `households/${user?.household_id}/members/list`,
      ),
    enabled: !!user?.household_id,
  });

  const currentMember =
    members?.find((m) => m.user_id === split.user_id) ?? null;

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button>Edit</Button>
      </PopoverTrigger>
      <PopoverContent align="end">
        <FieldGroup className="gap-4">
          <Field orientation="horizontal">
            <FieldLabel className="w-1/3">Member</FieldLabel>
            <Combobox
              value={currentMember}
              onValueChange={(member) => {
                if (member) {
                  onUpdate(split.id, {
                    user_id: member.user_id,
                    name: member.name,
                  });
                }
              }}
              items={members?.filter((m) => m.user_id !== user?.id)}
              itemToStringLabel={(member) => member!.name}
            >
              <ComboboxInput
                className="col-span-2"
                placeholder="Search members..."
              />
              <ComboboxContent className="pointer-events-auto">
                <ComboboxEmpty>No members found.</ComboboxEmpty>
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
          {split.split_type === "fixed" && (
            <Field orientation="horizontal">
              <FieldLabel className="w-1/3">Amount</FieldLabel>
              <Input
                className="col-span-2"
                type="number"
                value={split.amount}
                onChange={(e) =>
                  onUpdate(split.id, { amount: parseFloat(e.target.value) })
                }
              />
            </Field>
          )}
          {split.split_type === "percentage" && (
            <Field orientation="horizontal">
              <FieldLabel className="w-1/3">Percent Split</FieldLabel>
              <Input
                className="col-span-2"
                type="number"
                value={split.amount}
                onChange={(e) =>
                  onUpdate(split.id, { amount: parseFloat(e.target.value) })
                }
              />
            </Field>
          )}
        </FieldGroup>
      </PopoverContent>
    </Popover>
  );
}
