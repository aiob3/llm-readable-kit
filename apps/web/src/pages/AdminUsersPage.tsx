import { FormEvent, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

type Role = 'admin' | 'operator' | 'viewer';

interface UserItem {
  id: string;
  username: string;
  role: Role;
  created_at: string;
}

export function AdminUsersPage() {
  const [users, setUsers] = useState<UserItem[]>([]);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<Role>('viewer');
  const [error, setError] = useState('');

  async function load() {
    const response = await fetch('/api/admin/users', { credentials: 'include' });
    if (!response.ok) {
      throw new Error('Erro ao carregar usuários');
    }
    const data = (await response.json()) as { items: UserItem[] };
    setUsers(data.items);
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, []);

  async function onCreate(event: FormEvent) {
    event.preventDefault();
    setError('');

    const response = await fetch('/api/admin/users', {
      method: 'POST',
      credentials: 'include',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ username, password: password || undefined, role })
    });

    if (!response.ok) {
      setError('Falha ao criar usuário');
      return;
    }

    setUsername('');
    setPassword('');
    setRole('viewer');
    await load();
  }

  async function onResetPassword(id: string) {
    const response = await fetch(`/api/admin/users/${id}/reset-password`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({})
    });
    const data = await response.json();
    if (!response.ok) {
      setError('Falha ao resetar senha');
      return;
    }
    alert(`Senha temporária: ${data.temporaryPassword}`);
  }

  async function onChangeRole(id: string, newRole: Role) {
    const response = await fetch(`/api/admin/users/${id}/role`, {
      method: 'PATCH',
      credentials: 'include',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ role: newRole })
    });

    if (!response.ok) {
      setError('Falha ao atualizar role');
      return;
    }

    await load();
  }

  return (
    <div className="page">
      <header className="topbar">
        <h1>Admin · Usuários</h1>
        <div className="topbar-actions">
          <Link className="btn-link" to="/">Jobs</Link>
          <Link className="btn-link" to="/admin/integrations">Integrações</Link>
        </div>
      </header>

      <section className="card">
        <h2>Criar usuário</h2>
        <form onSubmit={onCreate} className="form-grid compact">
          <label htmlFor="new-username">Usuário</label>
          <input
            id="new-username"
            title="Usuário"
            placeholder="novo.usuario"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />

          <label htmlFor="new-password">Senha (opcional)</label>
          <input
            id="new-password"
            title="Senha"
            placeholder="deixe vazio para gerar"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <label htmlFor="new-role">Role</label>
          <select id="new-role" title="Role" value={role} onChange={(e) => setRole(e.target.value as Role)}>
            <option value="viewer">viewer</option>
            <option value="operator">operator</option>
            <option value="admin">admin</option>
          </select>

          <button type="submit">Criar</button>
        </form>
      </section>

      <section className="card mt-md">
        <h2>Usuários cadastrados</h2>
        {error ? <p className="error">{error}</p> : null}
        <table className="table">
          <thead>
            <tr>
              <th>Usuário</th>
              <th>Role</th>
              <th>Criado</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {users.map((item) => (
              <tr key={item.id}>
                <td>{item.username}</td>
                <td>{item.role}</td>
                <td>{new Date(item.created_at).toLocaleString()}</td>
                <td className="actions-inline">
                  <button onClick={() => onResetPassword(item.id)}>Resetar senha</button>
                  <button onClick={() => onChangeRole(item.id, 'viewer')}>viewer</button>
                  <button onClick={() => onChangeRole(item.id, 'operator')}>operator</button>
                  <button onClick={() => onChangeRole(item.id, 'admin')}>admin</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
