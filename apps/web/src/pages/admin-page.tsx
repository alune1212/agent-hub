import { Button, Card, CardContent, CardDescription, CardHeader, CardTitle } from "@internal/ui";

export function AdminPage(): JSX.Element {
  return (
    <Card>
      <CardHeader>
        <CardTitle>系统管理</CardTitle>
        <CardDescription>用户、角色、权限点配置入口。</CardDescription>
      </CardHeader>
      <CardContent className="flex gap-2">
        <Button>管理用户</Button>
        <Button variant="secondary">管理角色</Button>
        <Button variant="outline">管理权限点</Button>
      </CardContent>
    </Card>
  );
}
