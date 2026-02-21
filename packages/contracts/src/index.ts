// Shared types across gateway + web

export interface User {
  id: string;
  username: string;
  passwordHash: string;
  role: 'admin' | 'operator' | 'viewer';
  createdAt: Date;
  updatedAt: Date;
}

export interface Integration {
  id: string;
  name: string;
  type: 'http' | 'mcp' | 'cli';
  baseUrl?: string;
  headers?: Record<string, string>;
  secretName?: string;
  enabled: boolean;
  internalOnly?: boolean;
  mcpConfig?: {
    command: string;
    args: string[];
    env: Record<string, string>;
    transport: 'stdio' | 'http';
    allowlistTools?: string[];
  };
  createdAt: Date;
  updatedAt: Date;
}

export interface Job {
  id: string;
  type: string;
  status: 'pending' | 'running' | 'success' | 'failed';
  requestedBy: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface JobEvent {
  id: string;
  jobId: string;
  timestamp: Date;
  level: 'debug' | 'info' | 'warn' | 'error';
  message: string;
  payload?: Record<string, any>;
}

export interface Artifact {
  id: string;
  jobId: string;
  kind: string;
  path: string;
  mime: string;
  size: number;
  createdAt: Date;
}

// Auth types
export interface AuthLoginRequest {
  username: string;
  password: string;
}

export interface AuthLoginResponse {
  user: Omit<User, 'passwordHash'>;
  token: string;
}

export interface AuthMeResponse {
  user: Omit<User, 'passwordHash'>;
}

// Permissions matrix
export type Role = 'admin' | 'operator' | 'viewer';

export const PERMISSIONS: Record<Role, string[]> = {
  admin: ['manage:users', 'manage:integrations', 'run:jobs', 'view:jobs'],
  operator: ['manage:integrations', 'run:jobs', 'view:jobs'],
  viewer: ['view:jobs']
};

export function canPerform(role: Role, action: string): boolean {
  return PERMISSIONS[role].includes(action);
}

export function requiresRole(minRole: Role) {
  const roleHierarchy: Record<Role, number> = {
    admin: 3,
    operator: 2,
    viewer: 1
  };
  return (userRole: Role) => roleHierarchy[userRole] >= roleHierarchy[minRole];
}
