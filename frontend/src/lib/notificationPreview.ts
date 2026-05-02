import type {
  AppointmentPreview,
  NotificationPayload,
  PipelineResponse,
} from "@/types/pipeline";

export interface NotificationPreviewPayload {
  notification: NotificationPayload;
  appointment?: AppointmentPreview | Record<string, unknown>;
}

/** Returns payload when the pipeline included a notification slice worth showing. */
export function extractNotificationPreview(
  data: PipelineResponse,
): NotificationPreviewPayload | null {
  const n = data.notification;
  if (!n || typeof n !== "object") return null;
  const status = typeof n.status === "string" ? n.status : "";
  const message = typeof n.message === "string" ? n.message : "";
  const err = typeof n.error === "string" ? n.error : "";
  if (!status && !message.trim() && !err.trim()) return null;
  const appt = data.appointment;
  return {
    notification: n,
    appointment:
      appt && typeof appt === "object"
        ? (appt as AppointmentPreview | Record<string, unknown>)
        : undefined,
  };
}
