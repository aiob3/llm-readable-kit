import fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import type { FastifyInstance, FastifyReply, FastifyRequest } from 'fastify';
import { env } from '../config.js';
import { requirePermission } from '../security.js';

interface CreateJobBody {
  type: string;
  payload?: Record<string, unknown>;
}

function ensureArtifactsDir(jobId: string) {
  const folder = path.join(env.artifactsDir, jobId);
  if (!fs.existsSync(folder)) {
    fs.mkdirSync(folder, { recursive: true });
  }
  return folder;
}

export function registerJobRoutes(fastify: FastifyInstance) {
  fastify.get('/api/jobs', async (request: FastifyRequest, reply: FastifyReply) => {
    const user = requirePermission(fastify, request, reply, 'view:jobs');
    if (!user) return;

    const items = fastify.db
      .prepare('SELECT id, type, status, requested_by, created_at, updated_at FROM jobs ORDER BY created_at DESC')
      .all();

    return { items };
  });

  fastify.post<{ Body: CreateJobBody }>(
    '/api/jobs',
    async (request: FastifyRequest<{ Body: CreateJobBody }>, reply: FastifyReply) => {
      const user = requirePermission(fastify, request, reply, 'run:jobs');
      if (!user) return;

      const { type, payload = {} } = request.body ?? {};
      if (!type) {
        return reply.status(400).send({ error: 'type is required' });
      }

      const now = new Date().toISOString();
      const id = randomUUID();
      ensureArtifactsDir(id);

      fastify.db
        .prepare(
          `INSERT INTO jobs (id, type, status, requested_by, payload_json, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)`
        )
        .run(id, type, 'pending', user.username, JSON.stringify(payload), now, now);

      fastify.db
        .prepare(
          `INSERT INTO job_events (id, job_id, ts, level, message, payload_json)
           VALUES (?, ?, ?, ?, ?, ?)`
        )
        .run(randomUUID(), id, now, 'info', 'Job created', JSON.stringify(payload));

      return { id, type, status: 'pending', requestedBy: user.username, createdAt: now };
    }
  );

  fastify.get<{ Params: { id: string } }>(
    '/api/jobs/:id',
    async (request: FastifyRequest<{ Params: { id: string } }>, reply: FastifyReply) => {
      const user = requirePermission(fastify, request, reply, 'view:jobs');
      if (!user) return;

      const job = fastify.db
        .prepare('SELECT * FROM jobs WHERE id = ?')
        .get(request.params.id) as any;

      if (!job) {
        return reply.status(404).send({ error: 'job_not_found' });
      }

      const events = fastify.db
        .prepare('SELECT id, ts, level, message, payload_json FROM job_events WHERE job_id = ? ORDER BY ts ASC')
        .all(request.params.id);

      const artifacts = fastify.db
        .prepare('SELECT id, kind, path, mime, size, created_at FROM artifacts WHERE job_id = ? ORDER BY created_at ASC')
        .all(request.params.id);

      return {
        ...job,
        payload: job.payload_json ? JSON.parse(job.payload_json) : null,
        events: events.map((e: any) => ({
          ...e,
          payload: e.payload_json ? JSON.parse(e.payload_json) : null
        })),
        artifacts
      };
    }
  );

  fastify.get<{ Params: { id: string } }>(
    '/api/jobs/:id/events',
    async (request: FastifyRequest<{ Params: { id: string } }>, reply: FastifyReply) => {
      const user = requirePermission(fastify, request, reply, 'view:jobs');
      if (!user) return;

      const events = fastify.db
        .prepare('SELECT id, ts, level, message, payload_json FROM job_events WHERE job_id = ? ORDER BY ts ASC')
        .all(request.params.id);

      return {
        items: events.map((e: any) => ({
          ...e,
          payload: e.payload_json ? JSON.parse(e.payload_json) : null
        }))
      };
    }
  );
}
