import { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <div className="page"><p>Carregando sessão...</p></div>;
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  return <>{children}</>;
}
