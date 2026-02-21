import type { FastifyInstance, FastifyReply, FastifyRequest } from 'fastify';

export function registerHealthRoutes(fastify: FastifyInstance) {
  fastify.get('/health', async (_request: FastifyRequest, _reply: FastifyReply) => {
    return { status: 'ok' };
  });

  fastify.get('/health/readiness', async (_request: FastifyRequest, reply: FastifyReply) => {
    try {
      fastify.db.prepare('SELECT 1 as ok').get();
      return { ok: true, ready: true };
    } catch {
      return reply.status(503).send({ ok: false, ready: false });
    }
  });
}
