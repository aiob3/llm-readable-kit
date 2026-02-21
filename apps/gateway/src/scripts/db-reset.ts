import fs from 'node:fs';
import path from 'node:path';
import { env } from '../config.js';

function removeIfExists(target: string) {
  if (!fs.existsSync(target)) return;

  const stat = fs.statSync(target);
  if (stat.isDirectory()) {
    fs.rmSync(target, { recursive: true, force: true });
    return;
  }

  fs.rmSync(target, { force: true });
}

removeIfExists(env.dbPath);
removeIfExists(env.artifactsDir);

fs.mkdirSync(path.dirname(env.dbPath), { recursive: true });
fs.mkdirSync(env.artifactsDir, { recursive: true });

console.log(`Database reset complete: ${env.dbPath}`);
