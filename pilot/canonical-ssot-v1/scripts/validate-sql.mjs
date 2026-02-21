import fs from "node:fs";
import path from "node:path";

const sqlPath = path.resolve(process.cwd(), "sql/0001_canonical_core_event_log.sql");
const sql = fs.readFileSync(sqlPath, "utf8");

const mustContain = [
  "CREATE TABLE IF NOT EXISTS canonical_context",
  "CREATE TABLE IF NOT EXISTS canonical_identity",
  "CREATE TABLE IF NOT EXISTS canonical_role_catalog",
  "CREATE TABLE IF NOT EXISTS canonical_zone_catalog",
  "CREATE TABLE IF NOT EXISTS canonical_acl_binding",
  "CREATE TABLE IF NOT EXISTS canonical_event_log",
  "CREATE UNIQUE INDEX IF NOT EXISTS ux_canonical_event_log_idempotency_key",
  "USING GIN (payload_jsonb)"
];

const missing = mustContain.filter((snippet) => !sql.includes(snippet));

if (missing.length > 0) {
  console.error("SQL validation failed. Missing snippets:");
  for (const item of missing) {
    console.error(`- ${item}`);
  }
  process.exit(1);
}

console.log("SQL migration validation passed.");
