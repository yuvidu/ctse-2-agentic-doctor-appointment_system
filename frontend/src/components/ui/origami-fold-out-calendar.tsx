"use client";

import { Trash2 } from "lucide-react";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

export type FoldOutCalendarEvent = {
  id: string;
  title: string;
  date: Date;
};

export interface OrigamiFoldOutCalendarProps {
  events: FoldOutCalendarEvent[];
  onDeleteEvent?: (id: string) => void;
  /** Month shown in the accordion (year/month; day ignored). */
  displayedMonth: Date;
  /** Optional label above the fold-out. */
  monthLabel?: string;
}

export function OrigamiFoldOutCalendar({
  events,
  onDeleteEvent,
  displayedMonth,
  monthLabel,
}: OrigamiFoldOutCalendarProps) {
  const year = displayedMonth.getFullYear();
  const month = displayedMonth.getMonth();
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  const eventsByDate = (date: Date) =>
    events.filter((e) => e.date.toDateString() === date.toDateString());

  return (
    <div className="mas-panel-inner p-4">
      <h3 className="mb-3 font-semibold text-zinc-100">
        {monthLabel ??
          displayedMonth.toLocaleString("default", {
            month: "long",
            year: "numeric",
          })}
      </h3>

      <div className="h-[min(380px,50vh)] overflow-y-auto pr-2 md:h-[min(440px,52vh)]">
        <Accordion type="single" collapsible className="w-full">
          {Array.from({ length: daysInMonth }).map((_, i) => {
            const day = new Date(year, month, i + 1);
            const dayEvents = eventsByDate(day);

            return (
              <AccordionItem
                key={i}
                value={`day-${i}`}
                className="mb-2 overflow-hidden rounded-lg border border-white/10 !border-b-0 bg-zinc-950/40 last:mb-0"
              >
                <AccordionTrigger className="px-4 py-2.5 text-base font-semibold text-zinc-100 hover:no-underline [&[data-state=open]]:bg-white/5">
                  Day {i + 1} — {day.toDateString()}{" "}
                  {dayEvents.length > 0 ? `(${dayEvents.length} booked)` : ""}
                </AccordionTrigger>
                <AccordionContent className="space-y-2 border-t border-white/5 bg-black/20 px-4 py-3">
                  {dayEvents.length === 0 ? (
                    <p className="text-sm text-zinc-500">No bookings</p>
                  ) : (
                    dayEvents.map((ev) => (
                      <div
                        key={ev.id}
                        className="flex items-center justify-between rounded-lg border border-dashed border-white/15 bg-zinc-950/50 px-3 py-2.5 transition-transform hover:scale-[1.01]"
                      >
                        <span className="text-sm font-medium text-zinc-200">{ev.title}</span>
                        {onDeleteEvent ? (
                          <button
                            type="button"
                            className="rounded-md p-2 text-zinc-500 hover:bg-red-950/50 hover:text-red-300"
                            onClick={() => onDeleteEvent(ev.id)}
                            aria-label={`Remove booking ${ev.id}`}
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        ) : null}
                      </div>
                    ))
                  )}
                </AccordionContent>
              </AccordionItem>
            );
          })}
        </Accordion>
      </div>
    </div>
  );
}
