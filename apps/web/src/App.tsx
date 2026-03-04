import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "@/components/layout/app-layout";
import { ProtectedRoute } from "@/components/layout/protected-route";
import { AuditPage } from "@/pages/audit-page";
import { AdminPage } from "@/pages/admin-page";
import { BusinessPage } from "@/pages/business-page";
import { DashboardPage } from "@/pages/dashboard-page";
import { ForbiddenPage } from "@/pages/forbidden-page";
import { LoginPage } from "@/pages/login-page";
import { ReportsPage } from "@/pages/reports-page";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <ProtectedRoute permission="core:records:read">
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route
          path="/business"
          element={
            <ProtectedRoute permission="core:records:read">
              <BusinessPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/reports"
          element={
            <ProtectedRoute permission="reports:dashboard:read">
              <ReportsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/audit"
          element={
            <ProtectedRoute permission="audit:events:read">
              <AuditPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute permission="admin:users:read">
              <AdminPage />
            </ProtectedRoute>
          }
        />
      </Route>
      <Route path="/forbidden" element={<ForbiddenPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
