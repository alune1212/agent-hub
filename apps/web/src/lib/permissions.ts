export type AppRole = "employee" | "auditor" | "admin";

export const rolePermissions: Record<AppRole, string[]> = {
  employee: ["core:records:read", "core:records:create"],
  auditor: ["core:records:read", "audit:events:read", "reports:dashboard:read"],
  admin: [
    "core:records:read",
    "core:records:create",
    "audit:events:read",
    "reports:dashboard:read",
    "admin:users:read",
    "admin:users:write",
    "admin:roles:write"
  ]
};

export function can(permissions: string[], permission: string): boolean {
  return permissions.includes(permission);
}
