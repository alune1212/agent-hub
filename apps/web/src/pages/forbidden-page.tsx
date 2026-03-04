import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@internal/ui";

export function ForbiddenPage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>403</CardTitle>
        <CardDescription>当前角色无访问权限。</CardDescription>
      </CardHeader>
      <CardContent className="text-sm text-slate-500">
        请联系管理员分配对应权限点后再访问。
      </CardContent>
    </Card>
  );
}
