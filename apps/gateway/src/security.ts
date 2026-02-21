import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import type { FastifyReply, FastifyRequest } from 'fastify';
import type { FastifyInstance } from 'fastify';
import type { AuthUser, Role } from './db.js';

export const AUTH_COOKIE = 'auth_token';

const rolePermissions: Record<Role, string[]> = {
  admin: ['manage:users', 'manage:integrations', 'view:jobs', 'run:jobs'],
  operator: ['manage:integrations', 'view:jobs', 'run:jobs'],
  viewer: ['view:jobs']
};

interface JwtPayload {
  sub: string;
  username: string;
  role: Role;
}

export function hashPassword(password: string) {
  return bcrypt.hash(password, 10);
}

export function verifyPassword(password: string, hash: string) {
  return bcrypt.compare(password, hash);
}

export function signToken(user: AuthUser, secret: string) {
  const payload: JwtPayload = {
    sub: user.id,
    username: user.username,
    role: user.role
  };

  return jwt.sign(payload, secret, { expiresIn: '8h' });
}

export function verifyToken(token: string, secret: string) {
  return jwt.verify(token, secret) as JwtPayload;
}

export function setAuthCookie(reply: FastifyReply, token: string, secure: boolean) {
  reply.setCookie(AUTH_COOKIE, token, {
    httpOnly: true,
    secure,
    sameSite: 'lax',
    path: '/',
    maxAge: 60 * 60 * 8
  });
}

export function clearAuthCookie(reply: FastifyReply) {
  reply.clearCookie(AUTH_COOKIE, { path: '/' });
}

export function getUserFromRequest(fastify: FastifyInstance, request: FastifyRequest): AuthUser | null {
  const token = request.cookies[AUTH_COOKIE];
  if (!token) return null;

  try {
    const payload = verifyToken(token, fastify.env.jwtSecret);
    return {
      id: payload.sub,
      username: payload.username,
      role: payload.role
    };
  } catch {
    return null;
  }
}

export function requireAuth(
  fastify: FastifyInstance,
  request: FastifyRequest,
  reply: FastifyReply
) {
  const user = getUserFromRequest(fastify, request);
  if (!user) {
    reply.status(401).send({ error: 'unauthorized' });
    return null;
  }
  return user;
}

export function can(role: Role, permission: string) {
  return rolePermissions[role]?.includes(permission) ?? false;
}

export function requirePermission(
  fastify: FastifyInstance,
  request: FastifyRequest,
  reply: FastifyReply,
  permission: string
) {
  const user = requireAuth(fastify, request, reply);
  if (!user) return null;

  if (!can(user.role, permission)) {
    reply.status(403).send({ error: 'forbidden', permission });
    return null;
  }

  return user;
}
