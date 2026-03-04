import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

const API_BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://127.0.0.1:8000";
const TOKEN_KEY = "internal-platform-access-token";

export interface AuthUser {
  user_id: string;
  user_name: string;
  email: string | null;
  roles: string[];
  permissions: string[];
}

interface AuthContextValue {
  user: AuthUser | null;
  permissions: string[];
  loading: boolean;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function getStoredToken(): string | null {
  return window.localStorage.getItem(TOKEN_KEY);
}

function setStoredToken(token: string | null): void {
  if (!token) {
    window.localStorage.removeItem(TOKEN_KEY);
    return;
  }
  window.localStorage.setItem(TOKEN_KEY, token);
}

async function fetchMe(token: string | null): Promise<AuthUser> {
  const headers = new Headers();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}/api/v1/auth/me`, {
    method: "GET",
    headers,
    credentials: "include"
  });

  if (!response.ok) {
    throw new Error("Failed to load profile");
  }

  return (await response.json()) as AuthUser;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async (): Promise<void> => {
    const token = getStoredToken();
    try {
      const profile = await fetchMe(token);
      setUser(profile);
    } catch {
      setUser(null);
    }
  }, []);

  useEffect(() => {
    void (async () => {
      await refresh();
      setLoading(false);
    })();
  }, [refresh]);

  const login = useCallback(async (): Promise<void> => {
    setLoading(true);
    try {
      const loginResp = await fetch(
        `${API_BASE}/api/v1/auth/login?redirect_uri=${encodeURIComponent(window.location.origin)}`,
        {
          method: "GET",
          credentials: "include"
        }
      );
      if (!loginResp.ok) {
        throw new Error("Failed to start login");
      }

      const loginPayload = (await loginResp.json()) as { auth_url: string };
      const callbackUrl = new URL(loginPayload.auth_url, API_BASE).toString();
      const callbackResp = await fetch(callbackUrl, {
        method: "GET",
        credentials: "include"
      });
      if (!callbackResp.ok) {
        throw new Error("Failed to finish login");
      }

      const callbackPayload = (await callbackResp.json()) as {
        access_token: string;
        user: AuthUser;
      };
      setStoredToken(callbackPayload.access_token);
      setUser(callbackPayload.user);
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async (): Promise<void> => {
    const token = getStoredToken();
    const headers = new Headers();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    await fetch(`${API_BASE}/api/v1/auth/logout`, {
      method: "POST",
      headers,
      credentials: "include"
    });

    setStoredToken(null);
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      permissions: user?.permissions ?? [],
      loading,
      login,
      logout,
      refresh
    }),
    [loading, login, logout, refresh, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error("useAuth 必须在 AuthProvider 中调用");
  }
  return value;
}
