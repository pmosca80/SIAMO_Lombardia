import type { ReactNode } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { Layout } from "@/components/Layout";
import { HomePage } from "@/pages/HomePage";
import { LoginPage } from "@/pages/LoginPage";
import { RegisterPage } from "@/pages/RegisterPage";
import { ForgotPasswordPage } from "@/pages/ForgotPasswordPage";
import { ResetPasswordPage } from "@/pages/ResetPasswordPage";
import { VerificaPage } from "@/pages/VerificaPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { SociPage } from "@/pages/SociPage";
import { ComunicazioniPage } from "@/pages/ComunicazioniPage";
import { NotFoundPage } from "@/pages/NotFoundPage";

function Protetta({ children }: { children: ReactNode }) {
  return (
    <ProtectedRoute>
      <Layout>{children}</Layout>
    </ProtectedRoute>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/registrati" element={<RegisterPage />} />
        <Route path="/password-dimenticata" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/auth/verifica-email" element={<VerificaPage />} />

        <Route path="/" element={<HomePage />} />
        <Route
          path="/dashboard"
          element={
            <Protetta>
              <DashboardPage />
            </Protetta>
          }
        />
        <Route
          path="/soci"
          element={
            <Protetta>
              <SociPage />
            </Protetta>
          }
        />
        <Route
          path="/comunicazioni"
          element={
            <Protetta>
              <ComunicazioniPage />
            </Protetta>
          }
        />

        <Route path="/404" element={<NotFoundPage />} />
        <Route path="*" element={<Navigate to="/404" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
