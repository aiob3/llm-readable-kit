import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './auth/AuthContext';
import { LoginPage } from './pages/LoginPage';
import { JobsPage } from './pages/JobsPage';
import { AdminUsersPage } from './pages/AdminUsersPage';
import { AdminIntegrationsPage } from './pages/AdminIntegrationsPage';
import { ProtectedRoute } from './components/ProtectedRoute';
import { RoleRoute } from './components/RoleRoute';

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route
            path="/"
            element={
              <ProtectedRoute>
                <JobsPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/users"
            element={
              <ProtectedRoute>
                <RoleRoute allowedRoles={['admin']}>
                  <AdminUsersPage />
                </RoleRoute>
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/integrations"
            element={
              <ProtectedRoute>
                <RoleRoute allowedRoles={['admin', 'operator']}>
                  <AdminIntegrationsPage />
                </RoleRoute>
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
