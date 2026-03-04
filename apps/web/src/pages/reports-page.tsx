import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@internal/ui";

const weeklySeries = [
  { day: "Mon", value: 118 },
  { day: "Tue", value: 140 },
  { day: "Wed", value: 126 },
  { day: "Thu", value: 162 },
  { day: "Fri", value: 149 }
];

export function ReportsPage() {
  const maxValue = Math.max(...weeklySeries.map((item) => item.value));

  return (
    <Card>
      <CardHeader>
        <CardTitle>报表中心</CardTitle>
        <CardDescription>离线汇总数据（5 分钟增量任务）</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {weeklySeries.map((item) => (
            <div key={item.day} className="grid grid-cols-[40px_1fr_50px] items-center gap-3 text-sm">
              <span className="text-slate-500">{item.day}</span>
              <div className="h-2 rounded bg-slate-100">
                <div
                  className="h-2 rounded bg-slate-900"
                  style={{ width: `${(item.value / maxValue) * 100}%` }}
                />
              </div>
              <span>{item.value}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
