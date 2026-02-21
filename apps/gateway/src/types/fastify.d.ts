import type { AppEnv } from '../config.js';
import type { SqliteDb } from '../db.js';

declare module 'fastify' {
  interface FastifyInstance {
    db: SqliteDb;
    env: AppEnv;
  }
}
