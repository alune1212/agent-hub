import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";

import { useAuth } from "@/lib/auth";
import { can } from "@/lib/permissions";

export function ProtectedRoute({
  permission,
  children
}: {
  permission: string;
  children: ReactNode;
}) {
  const { loading, permissions, user } = useAuth();

  if (loading) {
    return <div className="p-6 text-sm text-slate-500">正在加载登录态...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (!can(permissions, permission)) {
    return <Navigate to="/forbidden" replace />;
  }

  return children;
}
