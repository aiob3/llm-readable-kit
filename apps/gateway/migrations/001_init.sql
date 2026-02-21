CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('admin', 'operator', 'viewer')),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS integrations (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('http', 'mcp', 'cli')),
  base_url TEXT,
  secret_ref TEXT,
  enabled INTEGER NOT NULL DEFAULT 1,
  config_json TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  status TEXT NOT NULL,
  requested_by TEXT NOT NULL,
  payload_json TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS job_events (
  id TEXT PRIMARY KEY,
  job_id TEXT NOT NULL,
  ts TEXT NOT NULL,
  level TEXT NOT NULL,
  message TEXT NOT NULL,
  payload_json TEXT,
  FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS artifacts (
  id TEXT PRIMARY KEY,
  job_id TEXT NOT NULL,
  kind TEXT NOT NULL,
  path TEXT NOT NULL,
  mime TEXT NOT NULL,
  size INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);
