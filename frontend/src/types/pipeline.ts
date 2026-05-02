/** Notification agent slice from `run_system` (mock send, skip, or failure). */
export interface NotificationPayload {
  /** `sent` | `failed` | `skipped` (no confirmed booking — no mock SMS) */
  status?: string;
  channel?: string | null;
  message?: string;
  error?: string | null;
}

/** Provisional or confirmed appointment row echoed to the UI. */
export interface AppointmentPreview {
  appointment_id?: string;
  user_name?: string;
  user_contact?: string;
  doctor?: string;
  specialization?: string;
  time_iso?: string;
  channel?: string;
}

/** Booking agent slice (local JSON commit; does not replace Intent ``status``). */
export interface BookingPayload {
  status?: string;
  appointment_id?: string;
  detail?: string;
}

/** Subset of `POST /api/pipeline` response used by the UI. */
export interface PipelineResponse {
  user_input?: string;
  status?: string;
  intent?: Record<string, unknown>;
  errors?: unknown[];
  availability_status?: string;
  availability_errors?: unknown[];
  booking?: BookingPayload;
  available_slots?: string[];
  availability?: {
    available_slots?: Array<{
      doctor_id?: string;
      start?: string;
      end?: string;
      location?: string;
      specialty?: string;
    }>;
    total_count?: number;
    ollama_ranking?: { rationale?: string; model?: string };
  };
  notification?: NotificationPayload;
  appointment?: AppointmentPreview | Record<string, unknown>;
}
