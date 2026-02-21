#!/usr/bin/env node
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(__dirname, "..");
const tsxBin = path.resolve(projectRoot, "node_modules", ".bin", "tsx");

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error("Usage: node scripts/run-tsx.mjs <entry.ts> [args...]");
  process.exit(1);
}

const child = spawn(tsxBin, args, {
  cwd: projectRoot,
  stdio: "inherit",
  env: {
    ...process.env,
    TMPDIR: process.env.TMPDIR || "/tmp"
  }
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exit(code ?? 1);
});
