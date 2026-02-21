import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { env } from './config.js';

const require = createRequire(import.meta.url);

export interface SqliteStatement {
  run: (...params: any[]) => any;
  get: (...params: any[]) => any;
  all: (...params: any[]) => any[];
}

export interface SqliteDb {
  prepare: (sql: string) => SqliteStatement;
  exec: (sql: string) => void;
  close: () => void;
  pragma?: (value: string) => void;
}

export type Role = 'admin' | 'operator' | 'viewer';

export interface DbUserRow {
  id: string;
  username: string;
  password_hash: string;
  role: Role;
  created_at: string;
  updated_at: string;
}

export interface AuthUser {
  id: string;
  username: string;
  role: Role;
}

function ensureDir(dir: string) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

export function initDb(): SqliteDb {
  ensureDir(env.dataDir);
  ensureDir(env.artifactsDir);

  let db: SqliteDb;

  try {
    const { DatabaseSync } = require('node:sqlite');
    const native = new DatabaseSync(env.dbPath);
    native.exec('PRAGMA journal_mode = WAL;');
    native.exec('PRAGMA foreign_keys = ON;');
    db = native;
  } catch {
    const BetterSqlite3 = require('better-sqlite3');
    const fallback = new BetterSqlite3(env.dbPath);
    fallback.pragma('journal_mode = WAL');
    fallback.pragma('foreign_keys = ON');
    db = fallback;
  }

  return db;
}

export function runMigrations(db: SqliteDb) {
  ensureDir(env.migrationsDir);

  db.exec(`
    CREATE TABLE IF NOT EXISTS migrations (
      name TEXT PRIMARY KEY,
      applied_at TEXT NOT NULL
    );
  `);

  const files = fs
    .readdirSync(env.migrationsDir)
    .filter((f: string) => f.endsWith('.sql'))
    .sort((a: string, b: string) => a.localeCompare(b));

  const alreadyApplied = db.prepare('SELECT name FROM migrations').all() as Array<{ name: string }>;
  const appliedSet = new Set(alreadyApplied.map((x) => x.name));

  const markApplied = db.prepare(
    'INSERT INTO migrations (name, applied_at) VALUES (?, ?)'
  );

  for (const file of files) {
    if (appliedSet.has(file)) continue;

    const sql = fs.readFileSync(path.join(env.migrationsDir, file), 'utf8');
    db.exec(sql);
    markApplied.run(file, new Date().toISOString());
  }
}

export function toPublicUser(row: DbUserRow): AuthUser {
  return {
    id: row.id,
    username: row.username,
    role: row.role
  };
}

