import { REQUIRED_EVENT_KEYS, REQUIRED_IAM_KEYS, ROLE_CATALOG, ZONE_CATALOG } from "./catalogs";
import { CanonicalError } from "./errors";
import { extractRoleCode, extractZoneLevel } from "./parser";
import type { CanonicalNormalized, RawCanonicalRecord } from "./types";
import { sha256Hex, stableStringify, utcNowIso } from "./utils";

export function normalizeCanonicalRecord(record: RawCanonicalRecord): CanonicalNormalized {
  const roleCode = extractRoleCode(record.c_con);
  const zoneLevel = extractZoneLevel(record.z_zon);
  const roleLabel = ROLE_CATALOG[roleCode];
  const zoneLabel = ZONE_CATALOG[zoneLevel];

  if (!roleLabel) {
    throw new CanonicalError("E_IAM_ROLE", "Role code is not mapped", { roleCode });
  }
  if (!zoneLabel) {
    throw new CanonicalError("E_IAM_ZONE", "Zone level is not mapped", { zoneLevel });
  }

  const normalizedNoMeta = {
    schema_version: "canonical-normalized.v1" as const,
    event_layer: REQUIRED_EVENT_KEYS.reduce(
      (acc, key) => {
        acc[key] = record[key];
        return acc;
      },
      {} as Record<(typeof REQUIRED_EVENT_KEYS)[number], string>
    ),
    iam_layer: REQUIRED_IAM_KEYS.reduce(
      (acc, key) => {
        acc[key] = record[key];
        return acc;
      },
      {} as Record<(typeof REQUIRED_IAM_KEYS)[number], string>
    ),
    catalog_resolution: {
      role_code: roleCode,
      role_label: roleLabel,
      zone_level: zoneLevel,
      zone_label: zoneLabel
    }
  };

  const payloadHash = sha256Hex(stableStringify(normalizedNoMeta));
  const idempotencyKey = sha256Hex(`${payloadHash}:canonical-normalized.v1`);

  return {
    ...normalizedNoMeta,
    metadata: {
      payload_hash: payloadHash,
      idempotency_key: idempotencyKey,
      normalized_at_utc: utcNowIso()
    }
  };
}
