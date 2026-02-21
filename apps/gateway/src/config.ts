import fs from 'node:fs';
import path from 'node:path';
import dotenv from 'dotenv';

function resolveRepoRoot() {
  const cwd = process.cwd();
  if (fs.existsSync(path.join(cwd, 'apps', 'gateway'))) {
    return cwd;
  }
  return path.resolve(cwd, '../..');
}

function toBool(value: string | undefined, fallback: boolean) {
  if (value == null) return fallback;
  return ['1', 'true', 'yes', 'on'].includes(value.toLowerCase());
}

export const repoRoot = resolveRepoRoot();
dotenv.config({ path: path.join(repoRoot, '.env') });

const rawDataDir = process.env.DATA_DIR ?? './data';
const dataDir = path.isAbsolute(rawDataDir)
  ? rawDataDir
  : path.resolve(repoRoot, rawDataDir);

export const env = {
  port: Number(process.env.PORT ?? 3333),
  webOrigin: process.env.WEB_ORIGIN ?? 'http://localhost:5173',
  jwtSecret: process.env.JWT_SECRET ?? 'dev-secret',
  cookieSecure: toBool(process.env.COOKIE_SECURE, false),
  dataDir,
  dbPath: path.join(dataDir, 'app.db'),
  artifactsDir: path.join(dataDir, 'artifacts'),
  migrationsDir: path.join(repoRoot, 'apps', 'gateway', 'migrations')
};

export type AppEnv = typeof env;
