import { Button, Card, CardContent, CardDescription, CardHeader, CardTitle } from "@internal/ui";

import { useAuth } from "@/lib/auth";

export function LoginPage() {
  const { loading, login } = useAuth();

  return (
    <div className="mx-auto mt-24 max-w-md">
      <Card>
        <CardHeader>
          <CardTitle>企业 SSO 登录</CardTitle>
          <CardDescription>点击后将走 SSO 登录流程（当前为 mock 模式）。</CardDescription>
        </CardHeader>
        <CardContent>
          <Button className="w-full" disabled={loading} onClick={() => void login()}>
            {loading ? "登录中..." : "使用企业账号登录"}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
