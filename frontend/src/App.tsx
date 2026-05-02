import { AppointmentsCalendar } from "@/components/AppointmentsCalendar";
import { NotificationPreviewDialog } from "@/components/NotificationPreviewDialog";
import Plan from "@/components/ui/agent-plan";
import { SmokeBackground } from "@/components/ui/spooky-smoke-animation";
import { VercelV0Chat } from "@/components/ui/v0-ai-chat";
import { SlotsDialog } from "@/components/SlotsDialog";
import {
  applyPipelineResultToTasks,
  freshHealthcareTasks,
  markPlanRunning,
} from "@/lib/syncPlanWithPipeline";
import { postPipeline } from "@/lib/api";
import { formatPipelineNetworkError } from "@/lib/pipelineErrors";
import { extractNotificationPreview } from "@/lib/notificationPreview";
import { extractSlotLines } from "@/lib/slotsFromPipeline";
import type { NotificationPreviewPayload } from "@/lib/notificationPreview";
import type { PipelineResponse } from "@/types/pipeline";
import type { Task } from "@/types/planTask";
import { useCallback, useEffect, useState } from "react";

export default function App() {
  const [planTasks, setPlanTasks] = useState<Task[]>(() => freshHealthcareTasks());
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastSummary, setLastSummary] = useState<string | null>(null);
  const [slotLines, setSlotLines] = useState<string[]>([]);
  const [slotsOpen, setSlotsOpen] = useState(false);
  const [notificationOpen, setNotificationOpen] = useState(false);
  const [notificationPreview, setNotificationPreview] =
    useState<NotificationPreviewPayload | null>(null);
  const [openNotificationAfterSlots, setOpenNotificationAfterSlots] = useState(false);
  const [calendarRefresh, setCalendarRefresh] = useState(0);

  useEffect(() => {
    if (!slotsOpen && openNotificationAfterSlots && notificationPreview) {
      setNotificationOpen(true);
      setOpenNotificationAfterSlots(false);
    }
  }, [slotsOpen, openNotificationAfterSlots, notificationPreview]);

  const onSend = useCallback(async (message: string) => {
    setError(null);
    setLastSummary(null);
    setSlotsOpen(false);
    setSlotLines([]);
    setNotificationOpen(false);
    setNotificationPreview(null);
    setOpenNotificationAfterSlots(false);
    setBusy(true);
    setPlanTasks((t) => markPlanRunning(t));
    try {
      const res = await postPipeline(message);
      const text = await res.text();
      let data: PipelineResponse = {};
      try {
        data = text ? (JSON.parse(text) as PipelineResponse) : {};
      } catch {
        setError("Invalid JSON from server.");
        setPlanTasks((t) => applyPipelineResultToTasks(t, {}));
        return;
      }
      if (!res.ok) {
        setError(
          typeof (data as { detail?: unknown }).detail === "string"
            ? (data as { detail: string }).detail
            : `Request failed (${res.status})`,
        );
        setPlanTasks((t) => applyPipelineResultToTasks(t, data));
        return;
      }
      setPlanTasks((t) => applyPipelineResultToTasks(t, data));
      setCalendarRefresh((n) => n + 1);

      const preview = extractNotificationPreview(data);
      setNotificationPreview(preview);

      const lines = extractSlotLines(data);
      setSlotLines(lines);
      if (lines.length > 0) {
        setSlotsOpen(true);
        setLastSummary(null);
        if (preview) setOpenNotificationAfterSlots(true);
      } else {
        setSlotsOpen(false);
        if (preview) {
          setLastSummary(null);
          setNotificationOpen(true);
        } else {
          setLastSummary(
            data.status === "complete"
              ? "No available slots for the requested filters."
              : "Intent needs more information or validation failed.",
          );
        }
      }
    } catch (e) {
      setError(formatPipelineNetworkError(e));
      setPlanTasks(freshHealthcareTasks);
    } finally {
      setBusy(false);
    }
  }, []);

  return (
    <div className="relative min-h-dvh w-full overflow-hidden">
      <div className="pointer-events-none fixed inset-0 z-0">
        <SmokeBackground smokeColor="#5b21b6" />
      </div>

      <div className="relative z-10 mx-auto w-full max-w-7xl px-4 py-6 md:px-6 md:py-8">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(300px,26rem)] lg:items-start lg:gap-x-10 lg:gap-y-0 xl:gap-x-12">
          <div className="flex min-h-0 min-w-0 flex-col gap-6 lg:gap-8">
            <main className="flex w-full flex-col items-center justify-center lg:min-h-[min(40vh,320px)]">
              <VercelV0Chat
                className="max-w-xl w-full md:max-w-lg lg:max-w-xl"
                onSend={onSend}
                disabled={busy}
                errorMessage={error}
                heading="Healthcare scheduling assistant"
                placeholder="e.g. I need a cardiologist in Colombo on 2026-05-02 morning…"
              />
              {lastSummary && !error ? (
                <p className="mt-4 max-w-xl px-2 text-center text-sm text-zinc-300">
                  {lastSummary}
                </p>
              ) : null}
            </main>

            <section className="mas-panel w-full" aria-label="Pipeline activity">
              <p className="mb-2 text-center text-[11px] font-semibold uppercase tracking-[0.14em] text-zinc-500">
                Pipeline activity
              </p>
              <div className="max-h-[min(320px,42vh)] overflow-y-auto pr-1 md:max-h-[min(400px,48vh)]">
                <Plan tasks={planTasks} onTasksChange={setPlanTasks} />
              </div>
            </section>
          </div>

          <section
            className="min-h-0 min-w-0 lg:sticky lg:top-6 lg:self-start"
            aria-label="Booked appointments"
          >
            <AppointmentsCalendar refreshTrigger={calendarRefresh} />
          </section>
        </div>
      </div>

      <SlotsDialog
        open={slotsOpen}
        lines={slotLines}
        onClose={() => setSlotsOpen(false)}
      />

      <NotificationPreviewDialog
        open={notificationOpen}
        notification={notificationPreview?.notification ?? null}
        appointment={notificationPreview?.appointment}
        onClose={() => setNotificationOpen(false)}
      />
    </div>
  );
}
