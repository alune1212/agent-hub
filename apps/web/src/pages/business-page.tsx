import { Button, Card, CardContent, CardDescription, CardHeader, CardTitle } from "@internal/ui";

import { useAuth } from "@/lib/auth";
import { can } from "@/lib/permissions";

export function BusinessPage(): JSX.Element {
  const { permissions } = useAuth();
  const canCreate = can(permissions, "core:records:create");

  return (
    <Card>
      <CardHeader>
        <CardTitle>业务功能</CardTitle>
        <CardDescription>演示按钮级权限：无权限用户不可操作“新增业务记录”。</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <Button disabled={!canCreate}>新增业务记录</Button>
        <p className="text-sm text-slate-500">
          {canCreate ? "当前角色有写权限。" : "当前角色无写权限（仅可读）。"}
        </p>
      </CardContent>
    </Card>
  );
}
