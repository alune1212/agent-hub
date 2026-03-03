import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@internal/ui";

const rows = [
  {
    id: "evt_001",
    actor: "u_admin",
    action: "admin.users.update_role",
    time: "2026-03-03 10:20:00"
  },
  {
    id: "evt_002",
    actor: "u_auditor",
    action: "audit.events.export",
    time: "2026-03-03 10:24:11"
  }
];

export function AuditPage(): JSX.Element {
  return (
    <Card>
      <CardHeader>
        <CardTitle>审计中心</CardTitle>
        <CardDescription>关键操作全量记录，append-only。</CardDescription>
      </CardHeader>
      <CardContent>
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b text-left text-slate-500">
              <th className="py-2">事件 ID</th>
              <th className="py-2">操作人</th>
              <th className="py-2">动作</th>
              <th className="py-2">时间</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id} className="border-b last:border-b-0">
                <td className="py-2">{row.id}</td>
                <td className="py-2">{row.actor}</td>
                <td className="py-2">{row.action}</td>
                <td className="py-2">{row.time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
}
