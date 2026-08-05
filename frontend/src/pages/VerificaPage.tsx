import { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { verificaEmail } from "@/api/auth";
import { useAuthStore } from "@/store/auth-store";
import { Card, CardBody } from "@/components/ui/Card";

export function VerificaPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const setTokens = useAuthStore((s) => s.setTokens);
  const [stato, setStato] = useState<"verifica" | "ok" | "errore">("verifica");
  const richiesto = useRef(false);

  useEffect(() => {
    if (!token || richiesto.current) return;
    richiesto.current = true;
    verificaEmail(token)
      .then((coppia) => {
        setTokens(coppia.access_token, coppia.refresh_token);
        setStato("ok");
        window.location.replace("/dashboard");
      })
      .catch(() => setStato("errore"));
  }, [token, setTokens]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-silver-100 p-4">
      <Card className="w-full max-w-sm">
        <CardBody className="text-center">
          {!token || stato === "errore" ? (
            <>
              <p className="text-sm text-tricolore-rosso">
                Link non valido o scaduto. Richiedine uno nuovo.
              </p>
              <Link to="/login" className="mt-3 inline-block text-sm text-brand-600 underline">
                Torna al login
              </Link>
            </>
          ) : (
            <p className="text-sm text-brand-950/70">Verifica dell'email in corso…</p>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
