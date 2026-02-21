import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

interface JobItem {
  id: string;
  type: string;
  status: string;
  requested_by: string;
  created_at: string;
}

export function JobsPage() {
  const { user, logout } = useAuth();
  const [items, setItems] = useState<JobItem[]>([]);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');

  async function loadJobs() {
    try {
      const response = await fetch('/api/jobs', { credentials: 'include' });
      if (!response.ok) throw new Error('Falha ao carregar jobs');
      const data = (await response.json()) as { items: JobItem[] };
      setItems(data.items);
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar jobs');
    }
  }

  useEffect(() => {
    loadJobs();
  }, []);

  async function createDemoJob() {
    setCreating(true);
    setError('');
    try {
      const response = await fetch('/api/jobs', {
        method: 'POST',
        credentials: 'include',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ type: 'demo', payload: { source: 'ui' } })
      });

      if (!response.ok) {
        throw new Error('Não foi possível criar job');
      }

      await loadJobs();
    } catch (err: any) {
      setError(err.message || 'Erro ao criar job');
    } finally {
      setCreating(false);
    }
  }

  async function doLogout() {
    await logout();
  }

  return (
    <div className="page">
      <header className="topbar">
        <h1>Dashboard de Jobs</h1>
        <div className="topbar-actions">
          <span className="badge">{user?.username} · {user?.role}</span>
          {(user?.role === 'admin' || user?.role === 'operator') && (
            <Link to="/admin/integrations" className="btn-link">Integrações</Link>
          )}
          {user?.role === 'admin' && (
            <Link to="/admin/users" className="btn-link">Usuários</Link>
          )}
          <button onClick={doLogout}>Sair</button>
        </div>
      </header>

      <section className="card">
        <div className="row-between">
          <h2>Jobs</h2>
          {(user?.role === 'admin' || user?.role === 'operator') && (
            <button onClick={createDemoJob} disabled={creating}>
              {creating ? 'Criando...' : 'Criar job de teste'}
            </button>
          )}
        </div>

        {error ? <p className="error">{error}</p> : null}

        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Tipo</th>
              <th>Status</th>
              <th>Solicitado por</th>
              <th>Criado em</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 ? (
              <tr>
                <td colSpan={5}>Nenhum job ainda.</td>
              </tr>
            ) : (
              items.map((item) => (
                <tr key={item.id}>
                  <td>{item.id.slice(0, 8)}...</td>
                  <td>{item.type}</td>
                  <td>{item.status}</td>
                  <td>{item.requested_by}</td>
                  <td>{new Date(item.created_at).toLocaleString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
}
