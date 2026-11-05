"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { apiClient } from "./api";
import type { Me } from "./types";

interface AuthContextValue {
  me: Me | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<Me>;
  register: (input: {
    name: string;
    email: string;
    password: string;
    org_name?: string;
  }) => Promise<Me>;
  demoLogin: () => Promise<Me>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [me, setMe] = useState<Me | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const data = await apiClient.me();
      setMe(data);
    } catch {
      setMe(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let alive = true;
    apiClient
      .me()
      .then((data) => {
        if (alive) setMe(data);
      })
      .catch(() => {
        if (alive) setMe(null);
      })
      .finally(() => {
        if (alive) setLoading(false);
      });
    return () => {
      alive = false;
    };
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const data = await apiClient.login({ email, password });
    setMe(data);
    return data;
  }, []);

  const register = useCallback(
    async (input: { name: string; email: string; password: string; org_name?: string }) => {
      const data = await apiClient.register(input);
      setMe(data);
      return data;
    },
    [],
  );

  const demoLogin = useCallback(async () => {
    const data = await apiClient.demo();
    setMe(data);
    return data;
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiClient.logout();
    } finally {
      setMe(null);
    }
  }, []);

  const value = useMemo(
    () => ({ me, loading, login, register, demoLogin, logout, refresh }),
    [me, loading, login, register, demoLogin, logout, refresh],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
