import type { FastifyInstance, FastifyReply, FastifyRequest } from 'fastify';
import type { DbUserRow } from '../db.js';
import {
  clearAuthCookie,
  getUserFromRequest,
  setAuthCookie,
  signToken,
  verifyPassword
} from '../security.js';

interface LoginBody {
  username: string;
  password: string;
}

export function registerAuthRoutes(fastify: FastifyInstance) {
  fastify.post<{ Body: LoginBody }>('/auth/login', async (
    request: FastifyRequest<{ Body: LoginBody }>,
    reply: FastifyReply
  ) => {
    const { username, password } = request.body ?? {};
    if (!username || !password) {
      return reply.status(400).send({ error: 'username and password are required' });
    }

    const user = fastify.db
      .prepare('SELECT * FROM users WHERE username = ?')
      .get(username) as DbUserRow | undefined;

    if (!user) {
      return reply.status(401).send({ error: 'invalid_credentials' });
    }

    const ok = await verifyPassword(password, user.password_hash);
    if (!ok) {
      return reply.status(401).send({ error: 'invalid_credentials' });
    }

    const authUser = { id: user.id, username: user.username, role: user.role };
    const token = signToken(authUser, fastify.env.jwtSecret);
    setAuthCookie(reply, token, fastify.env.cookieSecure);

    return { user: authUser };
  });

  fastify.post('/auth/logout', async (_request: FastifyRequest, reply: FastifyReply) => {
    clearAuthCookie(reply);
    return { ok: true };
  });

  fastify.get('/auth/me', async (request: FastifyRequest, reply: FastifyReply) => {
    const auth = getUserFromRequest(fastify, request);
    if (!auth) {
      return reply.status(401).send({ error: 'unauthorized' });
    }

    const user = fastify.db
      .prepare('SELECT id, username, role FROM users WHERE id = ?')
      .get(auth.id) as { id: string; username: string; role: string } | undefined;

    if (!user) {
      return reply.status(401).send({ error: 'unauthorized' });
    }

    return { user };
  });
}
