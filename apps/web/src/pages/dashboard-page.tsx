import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@internal/ui";

const kpiList = [
  { label: "活跃员工", value: "326" },
  { label: "今日关键操作", value: "1,204" },
  { label: "待处理审计告警", value: "7" }
];

export function DashboardPage(): JSX.Element {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      {kpiList.map((kpi) => (
        <Card key={kpi.label}>
          <CardHeader>
            <CardDescription>{kpi.label}</CardDescription>
            <CardTitle>{kpi.value}</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-slate-500">数据来自 reporting 汇总层</CardContent>
        </Card>
      ))}
    </div>
  );
}
