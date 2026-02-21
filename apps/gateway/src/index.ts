import Fastify from 'fastify';
import fastifyCookie from '@fastify/cookie';
import fastifyCors from '@fastify/cors';
import { env } from './config.js';
import { initDb, runMigrations } from './db.js';
import { registerHealthRoutes } from './routes/health.js';
import { registerAuthRoutes } from './routes/auth.js';
import { registerAdminUsersRoutes } from './routes/admin-users.js';
import { registerAdminIntegrationsRoutes } from './routes/admin-integrations.js';
import { registerJobRoutes } from './routes/jobs.js';

export async function createApp() {
  const app = Fastify({ logger: true });

  await app.register(fastifyCookie);
  await app.register(fastifyCors, {
    origin: env.webOrigin,
    credentials: true
  });

  const db = initDb();
  runMigrations(db);

  app.decorate('db', db);
  app.decorate('env', env);

  registerHealthRoutes(app);
  registerAuthRoutes(app);
  registerAdminUsersRoutes(app);
  registerAdminIntegrationsRoutes(app);
  registerJobRoutes(app);

  return app;
}

async function start() {
  const app = await createApp();
  await app.listen({ host: '0.0.0.0', port: env.port });
}

start().catch((error) => {
  console.error(error);
  process.exit(1);
});
