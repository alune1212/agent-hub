import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

import { rolePermissions, type AppRole } from "./permissions";

interface AuthContextValue {
  role: AppRole;
  permissions: string[];
  switchRole: (nextRole: AppRole) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const ROLE_KEY = "internal-platform-role";

function readInitialRole(): AppRole {
  const role = window.localStorage.getItem(ROLE_KEY);
  if (role === "employee" || role === "auditor" || role === "admin") {
    return role;
  }
  return "admin";
}

export function AuthProvider({ children }: { children: ReactNode }): JSX.Element {
  const [role, setRole] = useState<AppRole>(() => readInitialRole());

  const value = useMemo<AuthContextValue>(() => {
    return {
      role,
      permissions: rolePermissions[role],
      switchRole: (nextRole: AppRole) => {
        window.localStorage.setItem(ROLE_KEY, nextRole);
        setRole(nextRole);
      }
    };
  }, [role]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error("useAuth 必须在 AuthProvider 中调用");
  }
  return value;
}
