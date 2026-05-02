"use client";

import * as React from "react";
import { ChevronLeft, ChevronRight, Eraser, Loader2, RefreshCw } from "lucide-react";

import { OrigamiFoldOutCalendar } from "@/components/ui/origami-fold-out-calendar";
import type { FoldOutCalendarEvent } from "@/components/ui/origami-fold-out-calendar";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import {
  clearAllAppointments,
  deleteAppointment,
  fetchAppointments,
  type AppointmentRecord,
} from "@/lib/appointmentsApi";

const toolbarBtn =
  "border-white/15 bg-zinc-900/50 text-zinc-200 hover:bg-white/10 hover:text-white";

function recordsToEvents(rows: AppointmentRecord[]): FoldOutCalendarEvent[] {
  const out: FoldOutCalendarEvent[] = [];
  for (const r of rows) {
    const st = r.start_time;
    if (!st) continue;
    const d = new Date(st);
    if (Number.isNaN(d.getTime())) continue;
    const spec = (r.specialty || "").toString();
    const title = `${r.doctor_id ?? "?"}${spec ? ` · ${spec}` : ""} · ${r.id}`;
    out.push({ id: r.id, title, date: d });
  }
  return out;
}

export interface AppointmentsCalendarProps {
  /** Increment after a successful pipeline run to refresh the list. */
  refreshTrigger: number;
}

export function AppointmentsCalendar({ refreshTrigger }: AppointmentsCalendarProps) {
  const [displayedMonth, setDisplayedMonth] = React.useState(() => new Date());
  const [events, setEvents] = React.useState<FoldOutCalendarEvent[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [busy, setBusy] = React.useState(false);

  const load = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const rows = await fetchAppointments();
      setEvents(recordsToEvents(rows));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load appointments");
      setEvents([]);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    void load();
  }, [load, refreshTrigger]);

  const onDelete = async (id: string) => {
    setBusy(true);
    setError(null);
    try {
      await deleteAppointment(id);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Delete failed");
    } finally {
      setBusy(false);
    }
  };

  const onClearAll = async () => {
    if (!window.confirm("Remove all bookings from the local demo file?")) return;
    setBusy(true);
    setError(null);
    try {
      await clearAllAppointments();
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Clear failed");
    } finally {
      setBusy(false);
    }
  };

  const shiftMonth = (delta: number) => {
    setDisplayedMonth((d) => new Date(d.getFullYear(), d.getMonth() + delta, 1));
  };

  return (
    <div className="mas-panel flex flex-col gap-4">
      <div className="space-y-2 border-b border-white/10 pb-3">
        <h2 className="text-lg font-semibold tracking-tight text-zinc-100">Booked appointments</h2>
        <p className="text-xs leading-relaxed text-zinc-500">
          Live view of{" "}
          <code className="rounded border border-white/10 bg-black/30 px-1.5 py-0.5 font-mono text-[11px] text-zinc-400">
            data/appointments.json
          </code>{" "}
          — clear when re-testing the same slot.
        </p>
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <div className="flex items-center gap-1">
            <Button
              type="button"
              variant="outline"
              size="icon"
              className={toolbarBtn}
              aria-label="Previous month"
              onClick={() => shiftMonth(-1)}
              disabled={busy}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              type="button"
              variant="outline"
              size="icon"
              className={toolbarBtn}
              aria-label="Next month"
              onClick={() => shiftMonth(1)}
              disabled={busy}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="outline" size="sm" className={toolbarBtn} disabled={busy}>
                Jump to month…
              </Button>
            </PopoverTrigger>
            <PopoverContent
              className="w-auto border-white/10 bg-zinc-950 p-2 text-zinc-100 shadow-xl"
              align="start"
            >
              <Calendar
                mode="single"
                month={displayedMonth}
                onMonthChange={setDisplayedMonth}
                selected={undefined}
                onSelect={(d) => {
                  if (d) setDisplayedMonth(new Date(d.getFullYear(), d.getMonth(), 1));
                }}
              />
            </PopoverContent>
          </Popover>
          <Button
            type="button"
            variant="outline"
            size="sm"
            className={cn(toolbarBtn)}
            onClick={() => void load()}
            disabled={busy}
          >
            <RefreshCw className={cn("mr-1 h-4 w-4", loading && "animate-spin")} />
            Refresh
          </Button>
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="border-red-500/40 bg-red-950/30 text-red-200 hover:bg-red-900/40 hover:text-red-100"
            onClick={() => void onClearAll()}
            disabled={busy || events.length === 0}
          >
            <Eraser className="mr-1 h-4 w-4" />
            Clear all
          </Button>
          {busy ? <Loader2 className="h-4 w-4 animate-spin text-zinc-500" aria-hidden /> : null}
        </div>
      </div>

      {error ? (
        <p className="rounded-lg border border-red-500/35 bg-red-950/25 px-3 py-2 text-sm text-red-200">
          {error}
        </p>
      ) : null}

      {loading && events.length === 0 ? (
        <div className="flex items-center justify-center gap-2 py-10 text-zinc-500">
          <Loader2 className="h-5 w-5 animate-spin" />
          Loading…
        </div>
      ) : (
        <OrigamiFoldOutCalendar
          events={events}
          onDeleteEvent={(id) => void onDelete(id)}
          displayedMonth={displayedMonth}
        />
      )}
    </div>
  );
}
