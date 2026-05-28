import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

import type { User } from "./types";

type AuthCtx = {
  user: User | null;
  loading: boolean;
  signIn: () => Promise<void>;
  signOut: () => void;
};

const Ctx = createContext<AuthCtx | null>(null);

const STORAGE_KEY = "caros.auth.user";

const MOCK_USER: User = {
  id: "user-1",
  email: "alex@caros.dev",
  name: "Alex Morgan",
  avatarUrl: "https://api.dicebear.com/9.x/initials/svg?seed=Alex%20Morgan&backgroundColor=10b981",
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (raw) setUser(JSON.parse(raw));
    } catch {}
  }, []);

  const signIn = async () => {
    setLoading(true);
    await new Promise((r) => setTimeout(r, 800));
    setUser(MOCK_USER);
    try { window.localStorage.setItem(STORAGE_KEY, JSON.stringify(MOCK_USER)); } catch {}
    setLoading(false);
  };

  const signOut = () => {
    setUser(null);
    try { window.localStorage.removeItem(STORAGE_KEY); } catch {}
  };

  return <Ctx.Provider value={{ user, loading, signIn, signOut }}>{children}</Ctx.Provider>;
}

export function useAuth() {
  const v = useContext(Ctx);
  if (!v) throw new Error("useAuth outside AuthProvider");
  return v;
}
