/** Subset of `POST /api/pipeline` response used by the UI. */
export interface PipelineResponse {
  user_input?: string;
  status?: string;
  intent?: Record<string, unknown>;
  errors?: unknown[];
  availability_status?: string;
  availability_errors?: unknown[];
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
  appointment?: {
    id?: string;
    doctor_id?: string;
    start_time?: string;
    end_time?: string;
    location?: string;
    status?: string;
  };
}
