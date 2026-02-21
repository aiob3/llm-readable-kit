import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState
} from 'react';

type Role = 'admin' | 'operator' | 'viewer';

interface AuthUser {
  id: string;
  username: string;
  role: Role;
}

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

async function jsonRequest<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...init,
    credentials: 'include',
    headers: {
      'content-type': 'application/json',
      ...(init?.headers ?? {})
    }
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Request failed: ${response.status}`);
  }

  return (await response.json()) as T;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const result = await jsonRequest<{ user: AuthUser }>('/api/auth/me', { method: 'GET' });
      setUser(result.user);
    } catch {
      setUser(null);
    }
  }, []);

  useEffect(() => {
    refresh().finally(() => setLoading(false));
  }, [refresh]);

  const login = useCallback(async (username: string, password: string) => {
    await jsonRequest<{ user: AuthUser }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });

    await refresh();
  }, [refresh]);

  const logout = useCallback(async () => {
    await jsonRequest('/api/auth/logout', { method: 'POST' });
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ user, loading, login, logout, refresh }),
    [user, loading, login, logout, refresh]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return ctx;
}
