import { CanonicalError } from "./errors";
import type { CanonicalNormalized } from "./types";

export interface CanonicalEventRow {
  id: number;
  idempotency_key: string;
  payload_hash: string;
  payload_json: CanonicalNormalized;
  created_at: string;
  source: string;
}

/**
 * In-memory store used by tests and no-DB environments to validate idempotent behavior.
 */
export class InMemoryCanonicalEventStore {
  private rows = new Map<string, CanonicalEventRow>();
  private sequence = 0;

  upsertByIdempotency(payload: CanonicalNormalized, source = "canonical-cli"): CanonicalEventRow {
    const existing = this.rows.get(payload.metadata.idempotency_key);
    if (existing) {
      return existing;
    }

    this.sequence += 1;
    const created: CanonicalEventRow = {
      id: this.sequence,
      idempotency_key: payload.metadata.idempotency_key,
      payload_hash: payload.metadata.payload_hash,
      payload_json: payload,
      created_at: new Date().toISOString(),
      source
    };
    this.rows.set(payload.metadata.idempotency_key, created);
    return created;
  }

  getAll(): CanonicalEventRow[] {
    return [...this.rows.values()].sort((a, b) => b.id - a.id);
  }
}

export function assertIdempotencyKey(payload: CanonicalNormalized): void {
  if (!/^[a-f0-9]{64}$/.test(payload.metadata.idempotency_key)) {
    throw new CanonicalError("E_IDEMPOTENCY_FORMAT", "Invalid idempotency key format", {
      idempotency_key: payload.metadata.idempotency_key
    });
  }
}
