import { useEffect, useRef } from "react";
import {
  Bell,
  CalendarClock,
  CheckCircle2,
  Clock,
  HeartPulse,
  MinusCircle,
  Stethoscope,
  User,
  XCircle,
} from "lucide-react";
import type { AppointmentPreview, NotificationPayload } from "@/types/pipeline";

export interface NotificationPreviewDialogProps {
  open: boolean;
  notification: NotificationPayload | null;
  appointment?: AppointmentPreview | Record<string, unknown> | null;
  onClose: () => void;
}

function str(v: unknown): string | undefined {
  return typeof v === "string" && v.trim() ? v : undefined;
}

export function NotificationPreviewDialog({
  open,
  notification,
  appointment,
  onClose,
}: NotificationPreviewDialogProps) {
  const ref = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (open && notification) {
      if (!el.open) el.showModal();
    } else if (el.open) {
      el.close();
    }
  }, [open, notification]);

  if (!notification) return null;

  const sent = notification.status === "sent";
  const failed = notification.status === "failed";
  const skipped = notification.status === "skipped";
  const channel = (notification.channel ?? (skipped ? "—" : "message")).toString();
  const appt = appointment && typeof appointment === "object" ? appointment : null;

  return (
    <dialog
      ref={ref}
      className="w-[min(100%,26rem)] max-w-[calc(100vw-2rem)] overflow-hidden rounded-2xl border border-zinc-200/90 bg-white p-0 text-zinc-900 shadow-[0_25px_50px_-12px_rgba(0,0,0,0.25),0_0_0_1px_rgba(0,0,0,0.04)] backdrop:bg-black/50 backdrop:backdrop-blur-sm"
      onClose={onClose}
      onClick={(e) => {
        if (e.target === ref.current) {
          ref.current?.close();
        }
      }}
    >
      <div className="relative" onClick={(e) => e.stopPropagation()}>
        <div
          className="h-1 bg-gradient-to-r from-violet-600 via-fuchsia-500 to-violet-500"
          aria-hidden
        />
        <div className="p-5 md:p-6">
          <div className="mb-5 flex items-start justify-between gap-3">
            <div className="flex min-w-0 items-start gap-3">
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-violet-100 text-violet-600">
                <Bell className="h-5 w-5" strokeWidth={2} aria-hidden />
              </div>
              <div className="min-w-0 pt-0.5">
                <h2 className="text-base font-semibold tracking-tight text-zinc-900">
                  Notification preview
                </h2>
                <p className="mt-0.5 text-xs leading-relaxed text-zinc-500">
                  {skipped
                    ? "No SMS was sent — the appointment was not confirmed (e.g. slot already booked)."
                    : "Mock channel — same copy your agent would send after booking."}
                </p>
              </div>
            </div>
            <button
              type="button"
              className="shrink-0 rounded-lg px-2 py-1 text-sm font-medium text-zinc-500 transition hover:bg-zinc-100 hover:text-zinc-800"
              onClick={() => ref.current?.close()}
            >
              Close
            </button>
          </div>

          <div className="mb-4 flex flex-wrap items-center gap-2">
            <span
              className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium capitalize ${
                skipped
                  ? "border border-zinc-300 bg-zinc-100 text-zinc-700"
                  : "bg-zinc-700 text-white"
              }`}
            >
              {skipped ? "—" : channel}
            </span>
            {skipped ? (
              <span className="inline-flex items-center gap-1 rounded-full border border-zinc-300 bg-zinc-100 px-2.5 py-1 text-xs font-medium text-zinc-700">
                <MinusCircle className="h-3.5 w-3.5 text-zinc-500" aria-hidden />
                Skipped
              </span>
            ) : null}
            {sent ? (
              <span className="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" aria-hidden />
                Sent
              </span>
            ) : null}
            {failed ? (
              <span className="inline-flex items-center gap-1 rounded-full border border-rose-200 bg-rose-50 px-2.5 py-1 text-xs font-medium text-rose-700">
                <XCircle className="h-3.5 w-3.5 text-rose-600" aria-hidden />
                Failed
              </span>
            ) : null}
            {!sent && !failed && !skipped && notification.status ? (
              <span className="rounded-full border border-zinc-200 bg-zinc-50 px-2.5 py-1 text-xs font-medium text-zinc-600">
                {notification.status}
              </span>
            ) : null}
          </div>

          <div className="rounded-xl border border-zinc-200 bg-zinc-50/80 p-4 md:p-4">
            <p className="whitespace-pre-wrap text-[15px] leading-relaxed text-zinc-800">
              {notification.message?.trim()
                ? notification.message
                : "No message body returned."}
            </p>
          </div>

          {notification.error ? (
            <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2.5 text-sm text-amber-900">
              {notification.error}
            </div>
          ) : null}

          {appt ? (
            <div className="mt-5 rounded-xl bg-zinc-100 p-4 md:p-5">
              <p className="mb-4 text-[11px] font-semibold uppercase tracking-[0.12em] text-zinc-500">
                Appointment snapshot
              </p>
              <dl className="divide-y divide-zinc-200/80">
                {str(appt.appointment_id) ? (
                  <div className="flex items-center justify-between gap-4 py-3 first:pt-0">
                    <dt className="flex min-w-0 items-center gap-2 text-sm text-zinc-500">
                      <CalendarClock className="h-4 w-4 shrink-0 text-zinc-400" aria-hidden />
                      <span>ID</span>
                    </dt>
                    <dd className="text-right font-mono text-xs font-medium text-violet-600 sm:text-sm">
                      {str(appt.appointment_id)}
                    </dd>
                  </div>
                ) : null}
                {str(appt.doctor) ? (
                  <div className="flex items-center justify-between gap-4 py-3">
                    <dt className="flex items-center gap-2 text-sm text-zinc-500">
                      <Stethoscope className="h-4 w-4 shrink-0 text-zinc-400" aria-hidden />
                      Doctor
                    </dt>
                    <dd className="text-right text-sm font-medium text-zinc-900">
                      {str(appt.doctor)}
                    </dd>
                  </div>
                ) : null}
                {str(appt.specialization) ? (
                  <div className="flex items-center justify-between gap-4 py-3">
                    <dt className="flex items-center gap-2 text-sm text-zinc-500">
                      <HeartPulse className="h-4 w-4 shrink-0 text-zinc-400" aria-hidden />
                      Specialty
                    </dt>
                    <dd className="text-right text-sm font-medium text-zinc-900">
                      {str(appt.specialization)}
                    </dd>
                  </div>
                ) : null}
                {str(appt.time_iso) ? (
                  <div className="flex items-center justify-between gap-4 py-3">
                    <dt className="flex items-center gap-2 text-sm text-zinc-500">
                      <Clock className="h-4 w-4 shrink-0 text-zinc-400" aria-hidden />
                      Time
                    </dt>
                    <dd className="max-w-[58%] text-right text-xs font-medium leading-snug text-zinc-900 sm:text-sm">
                      {str(appt.time_iso)}
                    </dd>
                  </div>
                ) : null}
                {str(appt.user_name) || str(appt.user_contact) ? (
                  <div className="flex items-center justify-between gap-4 py-3 last:pb-0">
                    <dt className="flex items-center gap-2 text-sm text-zinc-500">
                      <User className="h-4 w-4 shrink-0 text-zinc-400" aria-hidden />
                      Patient
                    </dt>
                    <dd className="text-right text-sm font-medium text-zinc-900">
                      {[str(appt.user_name), str(appt.user_contact)].filter(Boolean).join(" · ")}
                    </dd>
                  </div>
                ) : null}
              </dl>
            </div>
          ) : null}
        </div>
      </div>
    </dialog>
  );
}
