import { Navigate } from "react-router-dom";

import { can } from "@/lib/permissions";
import { useAuth } from "@/lib/auth";

export function ProtectedRoute({
  permission,
  children
}: {
  permission: string;
  children: JSX.Element;
}): JSX.Element {
  const { permissions } = useAuth();

  if (!can(permissions, permission)) {
    return <Navigate to="/forbidden" replace />;
  }

  return children;
}
