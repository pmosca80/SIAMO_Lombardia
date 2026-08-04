import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuthStore } from "@/store/auth-store";

// La validità dell'access token è verificata dal backend ad ogni richiesta;
// se è scaduto l'interceptor in lib/api.ts prova a rinnovarlo con il
// refresh token prima di arrendersi (vedi ProtectedRoute + api.ts).
export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { accessToken, claims } = useAuthStore();

  if (!accessToken || !claims) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}
