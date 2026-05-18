import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";
import { useUser } from "@/hooks/useUser";
import API from "@/lib/api";
import type { ExpenseResponse } from "@/lib/types";
import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import React from "react";
import { CartesianGrid, Line, LineChart, XAxis } from "recharts";

interface DailyStats {
  date: string;
  total: number;
  yourExpenses: number;
  othersExpenses: number;
}

function RouteComponent() {
  const chartConfig = {
    total: {
      label: "Total",
      color: "var(--chart-1)",
    },
    yourExpenses: {
      label: "Your Expenses",
      color: "var(--chart-2)",
    },
    othersExpenses: {
      label: "Others Expenses",
      color: "var(--chart-3)",
    },
  } satisfies ChartConfig;

  const { user } = useUser();

  const [activeChart, setActiveChart] =
    React.useState<keyof typeof chartConfig>("total");

  const { data: expenses } = useQuery({
    queryKey: ["household-expenses"],
    queryFn: () =>
      API.req<ExpenseResponse[]>(
        `expenses/list?household_id=${user?.household_id}`,
      ),
    enabled: !!user?.household_id,
  });

  // Process expenses for the last month
  const chartData = React.useMemo(() => {
    if (!expenses || !user) return [];

    const now = new Date();
    const oneMonthAgo = new Date(now);
    oneMonthAgo.setMonth(now.getMonth() - 1);

    console.log(
      "All expenses:",
      expenses.map((e) => ({
        id: e.id,
        date: e.expense_date,
        amount: e.amount,
      })),
    );

    // Filter expenses from the last month
    const lastMonthExpenses = expenses.filter((expense) => {
      const expenseDate = new Date(expense.expense_date);
      return expenseDate >= oneMonthAgo && expenseDate <= now;
    });

    console.log(
      "Last month expenses:",
      lastMonthExpenses.map((e) => ({
        id: e.id,
        date: e.expense_date,
        amount: e.amount,
      })),
    );

    // Group expenses by date
    const dailyStats = new Map<string, DailyStats>();

    lastMonthExpenses.forEach((expense) => {
      // Normalize the date to YYYY-MM-DD format
      const expenseDate = new Date(expense.expense_date);
      const year = expenseDate.getFullYear();
      const month = String(expenseDate.getMonth() + 1).padStart(2, "0");
      const day = String(expenseDate.getDate()).padStart(2, "0");
      const dateKey = `${year}-${month}-${day}`;

      console.log(
        `Expense: id=${expense.id}, date=${expense.expense_date}, amount=${expense.amount}`,
      );

      const amount = parseFloat(expense.amount);
      const isUserExpense = expense.paid_by_id === user.id;

      if (!dailyStats.has(dateKey)) {
        dailyStats.set(dateKey, {
          date: dateKey,
          total: 0,
          yourExpenses: 0,
          othersExpenses: 0,
        });
      }

      const stats = dailyStats.get(dateKey)!;
      stats.total += amount;
      if (isUserExpense) {
        stats.yourExpenses += amount;
      } else {
        stats.othersExpenses += amount;
      }
    });

    // Convert to array and sort by date
    const result = Array.from(dailyStats.values()).sort(
      (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime(),
    );

    console.log("Chart data:", result);
    return result;
  }, [expenses, user]);

  const totals = React.useMemo(
    () => ({
      total: chartData.reduce((acc, curr) => acc + curr.total, 0),
      yourExpenses: chartData.reduce((acc, curr) => acc + curr.yourExpenses, 0),
      othersExpenses: chartData.reduce(
        (acc, curr) => acc + curr.othersExpenses,
        0,
      ),
    }),
    [chartData],
  );

  if (!user?.household_id) {
    return (
      <div className="h-full w-full p-5 flex items-center justify-center">
        <Card className="w-full h-full">
          <CardHeader>
            <CardTitle>No Household</CardTitle>
            <CardDescription>
              You need to be part of a household to view statistics.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  return (
    <div className="h-full w-full p-4">
      <Card className="h-full w-full">
        <CardHeader className="flex flex-col items-stretch border-b sm:flex-row">
          <div className="flex flex-1 flex-col justify-center gap-1 px-6 pb-3 sm:pb-0">
            <CardTitle>Household Statistics</CardTitle>
            <CardDescription>
              Showing expense breakdown for the last month
            </CardDescription>
          </div>
          <div className="flex">
            {(["total", "yourExpenses", "othersExpenses"] as const).map(
              (key) => {
                const chart = key as keyof typeof chartConfig;
                return (
                  <button
                    key={chart}
                    data-active={activeChart === chart}
                    className="flex flex-1 flex-col justify-center gap-1 border-t px-6 py-4 text-left even:border-l data-[active=true]:bg-muted/50 sm:border-t-0 sm:border-l sm:px-8 sm:py-6"
                    onClick={() => setActiveChart(chart)}
                  >
                    <span className="text-xs text-muted-foreground">
                      {chartConfig[chart].label}
                    </span>
                    <span className="text-lg font-bold leading-none sm:text-3xl">
                      ${totals[key].toFixed(2)}
                    </span>
                  </button>
                );
              },
            )}
          </div>
        </CardHeader>
        <CardContent className="h-full w-full px-2 sm:p-6">
          {chartData.length > 0 ? (
            <ChartContainer
              config={chartConfig}
              className="aspect-auto h-full w-full"
            >
              <LineChart
                accessibilityLayer
                data={chartData}
                margin={{
                  left: 12,
                  right: 12,
                }}
              >
                <CartesianGrid vertical={true} />
                <XAxis
                  dataKey="date"
                  tickLine={false}
                  axisLine={false}
                  tickMargin={8}
                  minTickGap={32}
                  tickFormatter={(value) => {
                    const date = new Date(value);
                    return date.toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                    });
                  }}
                />
                <ChartTooltip
                  content={
                    <ChartTooltipContent
                      className="w-37.5"
                      labelFormatter={(value) => {
                        return new Date(value).toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                        });
                      }}
                      formatter={(value) => `$${Number(value).toFixed(2)}`}
                    />
                  }
                />
                <Line
                  dataKey={activeChart}
                  type="monotone"
                  stroke={`var(--color-${activeChart})`}
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ChartContainer>
          ) : (
            <div className="flex h-full w-full items-center justify-center">
              <p className="text-muted-foreground">
                No expenses recorded in the last month
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export const Route = createFileRoute("/statistics")({
  component: RouteComponent,
});
