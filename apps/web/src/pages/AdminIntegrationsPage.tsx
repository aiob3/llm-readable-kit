import { FormEvent, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

type Kind = 'http' | 'mcp' | 'cli';

interface IntegrationItem {
  id: string;
  name: string;
  kind: Kind;
  base_url?: string | null;
  secret_ref?: string | null;
  config?: Record<string, unknown> | null;
  enabled: number;
}

export function AdminIntegrationsPage() {
  const [items, setItems] = useState<IntegrationItem[]>([]);
  const [name, setName] = useState('');
  const [kind, setKind] = useState<Kind>('http');
  const [baseUrl, setBaseUrl] = useState('');
  const [secretRef, setSecretRef] = useState('');
  const [enabled, setEnabled] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  async function load() {
    const response = await fetch('/api/admin/integrations', { credentials: 'include' });
    if (!response.ok) throw new Error('Falha ao carregar integrações');
    const data = (await response.json()) as { items: IntegrationItem[] };
    setItems(data.items);
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, []);

  async function onCreate(event: FormEvent) {
    event.preventDefault();
    setError('');
    setMessage('');

    const payload = {
      name,
      kind,
      baseUrl: baseUrl || undefined,
      secretRef: secretRef || undefined,
      enabled,
      config: kind === 'http' ? {} : { command: '' }
    };

    const response = await fetch('/api/admin/integrations', {
      method: 'POST',
      credentials: 'include',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      setError('Falha ao criar integração');
      return;
    }

    setName('');
    setKind('http');
    setBaseUrl('');
    setSecretRef('');
    setEnabled(true);
    await load();
  }

  async function onDelete(id: string) {
    const response = await fetch(`/api/admin/integrations/${id}`, {
      method: 'DELETE',
      credentials: 'include'
    });
    if (!response.ok) {
      setError('Falha ao remover integração');
      return;
    }
    await load();
  }

  async function onUpdate(item: IntegrationItem) {
    const newBaseUrl = window.prompt('Nova Base URL', item.base_url ?? '') ?? item.base_url ?? '';
    const newSecretRef = window.prompt('Novo Secret Ref', item.secret_ref ?? '') ?? item.secret_ref ?? '';

    const response = await fetch(`/api/admin/integrations/${item.id}`, {
      method: 'PUT',
      credentials: 'include',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        name: item.name,
        kind: item.kind,
        baseUrl: newBaseUrl || undefined,
        secretRef: newSecretRef || undefined,
        enabled: Boolean(item.enabled),
        config: item.config ?? {}
      })
    });

    if (!response.ok) {
      setError('Falha ao atualizar integração');
      return;
    }

    await load();
  }

  async function onTest(id: string) {
    setError('');
    setMessage('');

    const response = await fetch(`/api/admin/integrations/${id}/test`, {
      method: 'POST',
      credentials: 'include'
    });
    const data = await response.json();
    if (!response.ok || !data.ok) {
      setError(data.message || 'Integração indisponível');
      return;
    }

    setMessage(`Integração OK (status: ${data.status ?? 'validada'})`);
  }

  return (
    <div className="page">
      <header className="topbar">
        <h1>Admin · Integrações</h1>
        <div className="topbar-actions">
          <Link className="btn-link" to="/">Jobs</Link>
          <Link className="btn-link" to="/admin/users">Usuários</Link>
        </div>
      </header>

      <section className="card">
        <h2>Nova integração</h2>
        <form onSubmit={onCreate} className="form-grid compact">
          <label htmlFor="integration-name">Nome</label>
          <input
            id="integration-name"
            title="Nome da integração"
            placeholder="OpenAI API"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />

          <label htmlFor="integration-kind">Tipo</label>
          <select
            id="integration-kind"
            title="Tipo da integração"
            value={kind}
            onChange={(e) => setKind(e.target.value as Kind)}
          >
            <option value="http">http</option>
            <option value="mcp">mcp</option>
            <option value="cli">cli</option>
          </select>

          <label htmlFor="integration-url">Base URL</label>
          <input
            id="integration-url"
            title="Base URL"
            placeholder="http://127.0.0.1:8080/health"
            value={baseUrl}
            onChange={(e) => setBaseUrl(e.target.value)}
          />

          <label htmlFor="integration-secret">Secret Ref</label>
          <input
            id="integration-secret"
            title="Secret Ref"
            value={secretRef}
            onChange={(e) => setSecretRef(e.target.value)}
            placeholder="vault://my-key"
          />

          <label htmlFor="integration-enabled">
            <input
              id="integration-enabled"
              type="checkbox"
              checked={enabled}
              onChange={(e) => setEnabled(e.target.checked)}
            />{' '}
            habilitada
          </label>

          <button type="submit">Salvar</button>
        </form>
      </section>

      <section className="card mt-md">
        <h2>Integrações</h2>
        {error ? <p className="error">{error}</p> : null}
        {message ? <p className="success">{message}</p> : null}
        <table className="table">
          <thead>
            <tr>
              <th>Nome</th>
              <th>Tipo</th>
              <th>Base URL</th>
              <th>Secret Ref</th>
              <th>Status</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td>{item.name}</td>
                <td>{item.kind}</td>
                <td>{item.base_url ?? '-'}</td>
                <td>{item.secret_ref ?? '-'}</td>
                <td>{item.enabled ? 'on' : 'off'}</td>
                <td className="actions-inline">
                  <button onClick={() => onTest(item.id)}>Testar</button>
                  <button onClick={() => onUpdate(item)}>Atualizar</button>
                  <button onClick={() => onDelete(item.id)}>Remover</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
