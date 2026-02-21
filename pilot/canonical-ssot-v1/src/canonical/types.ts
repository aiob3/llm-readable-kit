import type { EventKey, IAMKey } from "./catalogs";

export type RawCanonicalRecord = Record<EventKey | IAMKey, string>;

export interface CanonicalNormalized {
  schema_version: "canonical-normalized.v1";
  event_layer: Record<EventKey, string>;
  iam_layer: Record<IAMKey, string>;
  catalog_resolution: {
    role_code: number;
    role_label: string;
    zone_level: number;
    zone_label: string;
  };
  metadata: {
    payload_hash: string;
    idempotency_key: string;
    normalized_at_utc: string;
  };
}
