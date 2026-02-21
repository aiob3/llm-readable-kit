import { initDb, runMigrations } from '../db.js';

const db = initDb();
runMigrations(db);
db.close();

console.log('Migrations applied successfully.');
