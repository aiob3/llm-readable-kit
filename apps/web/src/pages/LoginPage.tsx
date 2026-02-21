import { ChangeEvent, FormEvent, useState } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export function LoginPage() {
  const { user, login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  if (user) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(username, password);
      const from = (location.state as { from?: string } | null)?.from ?? '/';
      navigate(from, { replace: true });
    } catch (err: any) {
      setError('Credenciais inválidas');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page page-centered">
      <div className="card card-login">
        <h1>Login</h1>
        <p className="hint">Entre para acessar o dashboard.</p>

        <form onSubmit={handleSubmit} className="form-grid">
          <label htmlFor="username">Usuário</label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setUsername(e.target.value)}
            disabled={loading}
            placeholder="admin"
            required
          />

          <label htmlFor="password">Senha</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
            disabled={loading}
            placeholder="••••••••"
            required
          />

          {error ? <p className="error">{error}</p> : null}

          <button type="submit" disabled={loading}>
            {loading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>

        <p className="hint mt-sm">Login inicial: <strong>admin/admin123!</strong></p>
      </div>
    </div>
  );
}
