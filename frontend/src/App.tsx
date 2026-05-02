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

      <div className="relative z-10 mx-auto flex min-h-dvh max-w-7xl flex-col gap-4 p-3 md:flex-row md:p-6">
        <main className="flex flex-1 flex-col items-center justify-center">
          <VercelV0Chat
            onSend={onSend}
            disabled={busy}
            errorMessage={error}
            heading="Healthcare scheduling assistant"
            placeholder="e.g. I need a cardiologist in Colombo on 2026-05-02 morning…"
          />
          {lastSummary && !error ? (
            <p className="mt-4 max-w-xl text-center text-sm text-zinc-300">
              {lastSummary}
            </p>
          ) : null}
        </main>

        <aside className="w-full shrink-0 md:h-auto md:w-[380px] md:max-h-[calc(100dvh-3rem)]">
          <Plan tasks={planTasks} onTasksChange={setPlanTasks} />
        </aside>
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
