import { Calendar, CalendarDayButton } from "@/components/ui/calendar";
import { useUser } from "@/hooks/useUser";
import API from "@/lib/api";
import type { ExpenseResponse } from "@/lib/types";
import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import React from "react";

export const Route = createFileRoute("/calender")({
  component: RouteComponent,
});

function RouteComponent() {
  const { user } = useUser();

  const [date, setDate] = React.useState<Date | undefined>(new Date());
  const { data: expenses } = useQuery({
    queryKey: ["household-expenses"],
    queryFn: () =>
      API.req<ExpenseResponse[]>(
        `expenses/list?household_id=${user?.household_id}`,
      ),
    enabled: !!user?.household_id,
  });

  return (
    <div className="flex flex-col items-center justify-center w-full h-full p-4">
      <Calendar
        mode="single"
        selected={date}
        onSelect={setDate}
        className="rounded-lg border [--cell-size:--spacing(5)] md:[--cell-size:--spacing(5)] w-full h-full"
        captionLayout="dropdown"
        components={{
          DayButton: ({ children, modifiers, day, ...props }) => {
            const matchingExpenses = expenses?.filter(
              (e) =>
                new Date(e.expense_date).toDateString() ===
                day.date.toDateString(),
            );
            const isExpenseDay = (matchingExpenses?.length ?? 0) > 0;

            console.log("matchingExpenses", matchingExpenses);

            return (
              <CalendarDayButton day={day} modifiers={modifiers} {...props}>
                {children}
                {!modifiers.outside && isExpenseDay && (
                  <span>
                    Spent: £
                    {matchingExpenses?.reduce(
                      (acc, e) => acc + parseFloat(e.amount),
                      0,
                    )}
                  </span>
                )}
              </CalendarDayButton>
            );
          },
        }}
      />
    </div>
  );
}
