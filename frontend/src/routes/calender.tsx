import { Calendar } from "@/components/ui/calendar";
import { createFileRoute } from "@tanstack/react-router";
import React from "react";
export const Route = createFileRoute("/calender")({
  component: RouteComponent,
});

function RouteComponent() {
  const [date, setDate] = React.useState<Date | undefined>(new Date());
  return (
    <div className="flex flex-col items-center justify-center w-full h-full p-4">
      <Calendar
        mode="single"
        selected={date}
        onSelect={setDate}
        className="rounded-lg border [--cell-size:--spacing(5)] md:[--cell-size:--spacing(5)] w-full h-full"
        captionLayout="dropdown"
      />
    </div>
  );
}
