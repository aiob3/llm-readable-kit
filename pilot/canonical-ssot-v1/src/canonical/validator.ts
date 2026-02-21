import fs from "node:fs";
import path from "node:path";
import Ajv2020 from "ajv/dist/2020";
import addFormats from "ajv-formats";
import { CanonicalError } from "./errors";
import type { CanonicalNormalized } from "./types";

const ajv = new Ajv2020({ allErrors: true, strict: false });
addFormats(ajv);

export function validateCanonicalJson(
  payload: CanonicalNormalized,
  schemaPath = path.resolve(process.cwd(), "schema/canonical-normalized.v1.schema.json")
): true {
  const schemaRaw = fs.readFileSync(schemaPath, "utf8");
  const schema = JSON.parse(schemaRaw) as object;
  const validate = ajv.compile(schema);
  const valid = validate(payload);

  if (!valid) {
    throw new CanonicalError("E_SCHEMA_VALIDATION", "Payload does not match canonical schema", {
      errors: validate.errors ?? []
    });
  }

  return true;
}
