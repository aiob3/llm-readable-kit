import { randomUUID } from 'node:crypto';
import type { FastifyInstance, FastifyReply, FastifyRequest } from 'fastify';
import { requirePermission } from '../security.js';

type IntegrationKind = 'http' | 'mcp' | 'cli';

interface IntegrationInput {
  name: string;
  kind: IntegrationKind;
  baseUrl?: string;
  secretRef?: string;
  enabled?: boolean;
  config?: Record<string, unknown>;
}

export function registerAdminIntegrationsRoutes(fastify: FastifyInstance) {
  fastify.get('/admin/integrations', async (request: FastifyRequest, reply: FastifyReply) => {
    const user = requirePermission(fastify, request, reply, 'manage:integrations');
    if (!user) return;

    const items = fastify.db
      .prepare('SELECT * FROM integrations ORDER BY created_at DESC')
      .all();

    return {
      items: items.map((item: any) => ({
        ...item,
        config: item.config_json ? JSON.parse(item.config_json) : null
      }))
    };
  });

  fastify.post<{ Body: IntegrationInput }>(
    '/admin/integrations',
    async (request: FastifyRequest<{ Body: IntegrationInput }>, reply: FastifyReply) => {
      const user = requirePermission(fastify, request, reply, 'manage:integrations');
      if (!user) return;

      const { name, kind, baseUrl, secretRef, enabled = true, config } = request.body;
      if (!name || !kind) {
        return reply.status(400).send({ error: 'name and kind are required' });
      }

      const id = randomUUID();
      const now = new Date().toISOString();
      fastify.db
        .prepare(
          `INSERT INTO integrations
           (id, name, kind, base_url, secret_ref, enabled, config_json, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
        )
        .run(
          id,
          name,
          kind,
          baseUrl ?? null,
          secretRef ?? null,
          enabled ? 1 : 0,
          config ? JSON.stringify(config) : null,
          now,
          now
        );

      return { ok: true, id };
    }
  );

  fastify.put<{ Params: { id: string }; Body: IntegrationInput }>(
    '/admin/integrations/:id',
    async (
      request: FastifyRequest<{ Params: { id: string }; Body: IntegrationInput }>,
      reply: FastifyReply
    ) => {
      const user = requirePermission(fastify, request, reply, 'manage:integrations');
      if (!user) return;

      const { id } = request.params;
      const { name, kind, baseUrl, secretRef, enabled = true, config } = request.body;

      const result = fastify.db
        .prepare(
          `UPDATE integrations
           SET name = ?, kind = ?, base_url = ?, secret_ref = ?, enabled = ?, config_json = ?, updated_at = ?
           WHERE id = ?`
        )
        .run(
          name,
          kind,
          baseUrl ?? null,
          secretRef ?? null,
          enabled ? 1 : 0,
          config ? JSON.stringify(config) : null,
          new Date().toISOString(),
          id
        );

      if (result.changes === 0) {
        return reply.status(404).send({ error: 'integration_not_found' });
      }

      return { ok: true };
    }
  );

  fastify.delete<{ Params: { id: string } }>(
    '/admin/integrations/:id',
    async (request: FastifyRequest<{ Params: { id: string } }>, reply: FastifyReply) => {
      const user = requirePermission(fastify, request, reply, 'manage:integrations');
      if (!user) return;

      const result = fastify.db.prepare('DELETE FROM integrations WHERE id = ?').run(request.params.id);
      if (result.changes === 0) {
        return reply.status(404).send({ error: 'integration_not_found' });
      }

      return { ok: true };
    }
  );

  fastify.post<{ Params: { id: string } }>(
    '/admin/integrations/:id/test',
    async (request: FastifyRequest<{ Params: { id: string } }>, reply: FastifyReply) => {
      const user = requirePermission(fastify, request, reply, 'manage:integrations');
      if (!user) return;

      const integration = fastify.db
        .prepare('SELECT * FROM integrations WHERE id = ?')
        .get(request.params.id) as any;

      if (!integration) {
        return reply.status(404).send({ error: 'integration_not_found' });
      }

      if (integration.kind === 'http') {
        if (!integration.base_url) {
          return reply.status(400).send({ ok: false, message: 'base_url is required for http integrations' });
        }

        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 4000);
        try {
          const result = await fetch(integration.base_url, {
            method: 'GET',
            signal: controller.signal
          });
          clearTimeout(timeout);
          return { ok: result.ok, status: result.status };
        } catch (error) {
          clearTimeout(timeout);
          return reply.status(502).send({ ok: false, message: 'http integration failed' });
        }
      }

      const cfg = integration.config_json ? JSON.parse(integration.config_json) : {};
      if (integration.kind === 'mcp') {
        return {
          ok: !!cfg.command,
          message: cfg.command ? 'mcp config looks valid' : 'missing mcp command'
        };
      }

      return {
        ok: !!cfg.command,
        message: cfg.command ? 'cli config looks valid' : 'missing cli command'
      };
    }
  );
}
