import { getApiBase } from "@/lib/api";

export type AppointmentRecord = {
  id: string;
  doctor_id?: string;
  start_time?: string;
  end_time?: string;
  specialty?: string;
  location?: string;
  status?: string;
  user_intent?: string;
};

export async function fetchAppointments(): Promise<AppointmentRecord[]> {
  const base = getApiBase();
  const res = await fetch(`${base}/api/appointments`);
  if (!res.ok) {
    throw new Error(`appointments ${res.status}`);
  }
  const data = (await res.json()) as { appointments?: unknown };
  const raw = data.appointments;
  if (!Array.isArray(raw)) return [];
  return raw.filter((x): x is AppointmentRecord => typeof x === "object" && x !== null && "id" in x) as AppointmentRecord[];
}

export async function deleteAppointment(id: string): Promise<void> {
  const base = getApiBase();
  const res = await fetch(`${base}/api/appointments/${encodeURIComponent(id)}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    throw new Error(`delete ${res.status}`);
  }
}

export async function clearAllAppointments(): Promise<void> {
  const base = getApiBase();
  const res = await fetch(`${base}/api/appointments/clear`, { method: "POST" });
  if (!res.ok) {
    throw new Error(`clear ${res.status}`);
  }
}
