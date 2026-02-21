import { randomUUID } from 'node:crypto';
import { initDb, runMigrations } from '../db.js';
import { hashPassword } from '../security.js';

async function seed() {
  const db = initDb();
  runMigrations(db);

  const exists = db
    .prepare('SELECT id FROM users WHERE username = ?')
    .get('admin') as { id: string } | undefined;

  if (exists) {
    db.close();
    console.log('Admin user already exists.');
    return;
  }

  const now = new Date().toISOString();
  const passwordHash = await hashPassword('admin123!');

  db.prepare(
    `INSERT INTO users (id, username, password_hash, role, created_at, updated_at)
     VALUES (?, ?, ?, ?, ?, ?)`
  ).run(randomUUID(), 'admin', passwordHash, 'admin', now, now);

  db.close();
  console.warn('⚠️ Seed complete: login admin/admin123! and change password immediately.');
}

seed().catch((error) => {
  console.error(error);
  process.exit(1);
});
