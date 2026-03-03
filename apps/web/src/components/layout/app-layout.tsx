import { NavLink, Outlet } from "react-router-dom";

import { Badge, Button } from "@internal/ui";

import { useAuth } from "@/lib/auth";
import type { AppRole } from "@/lib/permissions";

const roleOptions: AppRole[] = ["employee", "auditor", "admin"];

export function AppLayout(): JSX.Element {
  const { role, switchRole } = useAuth();
  const navItems = [
    { to: "/", label: "工作台", end: true },
    { to: "/business", label: "业务功能" },
    { to: "/reports", label: "报表中心" },
    { to: "/audit", label: "审计中心" },
    { to: "/admin", label: "系统管理" },
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div>
            <p className="text-xs uppercase tracking-wider text-slate-500">Internal Platform</p>
            <h1 className="text-xl font-semibold">管理与审计系统</h1>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="secondary">当前角色：{role}</Badge>
            {roleOptions.map((roleOption) => (
              <Button
                key={roleOption}
                variant={roleOption === role ? "default" : "outline"}
                size="sm"
                onClick={() => switchRole(roleOption)}
              >
                切换为 {roleOption}
              </Button>
            ))}
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-7xl grid-cols-1 gap-6 px-6 py-6 lg:grid-cols-[220px_1fr]">
        <aside className="rounded-xl border bg-white p-3">
          <nav className="flex flex-col gap-1 text-sm">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                className={({ isActive }) =>
                  isActive
                    ? "rounded-md bg-slate-900 px-3 py-2 text-slate-50"
                    : "rounded-md px-3 py-2 hover:bg-slate-100"
                }
                end={item.end}
                to={item.to}
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </aside>
        <section>
          <Outlet />
        </section>
      </main>
    </div>
  );
}
