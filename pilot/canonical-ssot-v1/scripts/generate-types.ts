import fs from "node:fs";
import path from "node:path";

const schemaPath = path.resolve(process.cwd(), "schema/canonical-normalized.v1.schema.json");
const outputPath = path.resolve(process.cwd(), "src/shared/schema/generated-types.ts");

const schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));

function readRequiredKeys(section: string): string[] {
  return schema.properties?.[section]?.required ?? [];
}

const eventKeys = readRequiredKeys("event_layer");
const iamKeys = readRequiredKeys("iam_layer");

const content = `/* eslint-disable */
// AUTO-GENERATED FILE. Source: schema/canonical-normalized.v1.schema.json

export type CanonicalEventKey = ${eventKeys.map((key) => `"${key}"`).join(" | ")};
export type CanonicalIAMKey = ${iamKeys.map((key) => `"${key}"`).join(" | ")};

export type CanonicalEventV1 = Record<CanonicalEventKey, string>;
export type CanonicalIAMV1 = Record<CanonicalIAMKey, string>;

export interface CanonicalContextV1 {
  schema_version: "canonical-normalized.v1";
  event_layer: CanonicalEventV1;
  iam_layer: CanonicalIAMV1;
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
`;

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, content, "utf8");
console.log(`Generated types: ${outputPath}`);
