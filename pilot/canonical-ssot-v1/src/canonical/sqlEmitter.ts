import fs from "node:fs";
import path from "node:path";

const MIGRATION_SOURCE = path.resolve(process.cwd(), "sql/0001_canonical_core_event_log.sql");

export function emitCanonicalSql(outputPath: string): void {
  const sql = fs.readFileSync(MIGRATION_SOURCE, "utf8");
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, sql, "utf8");
}
