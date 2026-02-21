import { randomUUID } from 'node:crypto';
import type { FastifyInstance, FastifyReply, FastifyRequest } from 'fastify';
import { hashPassword, requirePermission } from '../security.js';
import type { Role } from '../db.js';

interface CreateUserBody {
  username: string;
  password?: string;
  role: Role;
}

interface UpdateRoleBody {
  role: Role;
}

interface ResetPasswordBody {
  newPassword?: string;
}

function randomPassword() {
  return Math.random().toString(36).slice(-10) + 'A!';
}

export function registerAdminUsersRoutes(fastify: FastifyInstance) {
  fastify.get('/admin/users', async (request: FastifyRequest, reply: FastifyReply) => {
    const user = requirePermission(fastify, request, reply, 'manage:users');
    if (!user) return;

    const rows = fastify.db
      .prepare('SELECT id, username, role, created_at, updated_at FROM users ORDER BY username')
      .all();

    return { items: rows };
  });

  fastify.post<{ Body: CreateUserBody }>(
    '/admin/users',
    async (request: FastifyRequest<{ Body: CreateUserBody }>, reply: FastifyReply) => {
      const actor = requirePermission(fastify, request, reply, 'manage:users');
      if (!actor) return;

      const { username, role } = request.body;
      const password = request.body.password || randomPassword();
      if (!username || !role) {
        return reply.status(400).send({ error: 'username and role are required' });
      }

      const now = new Date().toISOString();
      try {
        fastify.db
          .prepare(
            `INSERT INTO users (id, username, password_hash, role, created_at, updated_at)
             VALUES (?, ?, ?, ?, ?, ?)`
          )
          .run(randomUUID(), username, await hashPassword(password), role, now, now);
      } catch {
        return reply.status(409).send({ error: 'username_already_exists' });
      }

      return { ok: true, warning: request.body.password ? undefined : 'temporary_password_generated' };
    }
  );

  fastify.patch<{ Params: { id: string }; Body: UpdateRoleBody }>(
    '/admin/users/:id/role',
    async (
      request: FastifyRequest<{ Params: { id: string }; Body: UpdateRoleBody }>,
      reply: FastifyReply
    ) => {
      const actor = requirePermission(fastify, request, reply, 'manage:users');
      if (!actor) return;

      const { id } = request.params;
      const { role } = request.body;
      if (!role) {
        return reply.status(400).send({ error: 'role is required' });
      }

      const result = fastify.db
        .prepare('UPDATE users SET role = ?, updated_at = ? WHERE id = ?')
        .run(role, new Date().toISOString(), id);

      if (result.changes === 0) {
        return reply.status(404).send({ error: 'user_not_found' });
      }

      return { ok: true };
    }
  );

  fastify.post<{ Params: { id: string }; Body: ResetPasswordBody }>(
    '/admin/users/:id/reset-password',
    async (
      request: FastifyRequest<{ Params: { id: string }; Body: ResetPasswordBody }>,
      reply: FastifyReply
    ) => {
      const actor = requirePermission(fastify, request, reply, 'manage:users');
      if (!actor) return;

      const { id } = request.params;
      const newPassword = request.body?.newPassword || randomPassword();

      const result = fastify.db
        .prepare('UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?')
        .run(await hashPassword(newPassword), new Date().toISOString(), id);

      if (result.changes === 0) {
        return reply.status(404).send({ error: 'user_not_found' });
      }

      return {
        ok: true,
        temporaryPassword: newPassword,
        warning: 'force user to change password on first login'
      };
    }
  );
}
