import { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

type Role = 'admin' | 'operator' | 'viewer';

export function RoleRoute({
  children,
  allowedRoles
}: {
  children: ReactNode;
  allowedRoles: Role[];
}) {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (!allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}
