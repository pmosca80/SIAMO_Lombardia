import { useState, type FormEvent } from "react";
import { Navigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { richiediMagicLink } from "@/api/auth";
import { useAuthStore } from "@/store/auth-store";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card, CardBody } from "@/components/ui/Card";
import logo from "@/assets/logo.jpg";
import sfondo from "@/assets/sfondo.jpg";

export function LoginPage() {
  const [email, setEmail] = useState("");
  const accessToken = useAuthStore((s) => s.accessToken);

  const mutation = useMutation({ mutationFn: richiediMagicLink });

  if (accessToken) {
    return <Navigate to="/" replace />;
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    mutation.mutate(email);
  }

  return (
    <div
      className="flex min-h-screen items-center justify-center bg-cover bg-center p-4"
      style={{ backgroundImage: `url(${sfondo})` }}
    >
      <Card className="w-full max-w-sm bg-white/95 backdrop-blur">
        <CardBody className="flex flex-col items-center gap-6">
          <img src={logo} alt="S.I.A.M.O. Esercito Lombardia" className="h-24 w-24" />
          <div className="text-center">
            <h1 className="text-lg font-semibold text-brand-950">S.I.A.M.O. Esercito</h1>
            <p className="text-sm text-brand-950/60">Area riservata iscritti · Lombardia</p>
          </div>

          {mutation.isSuccess ? (
            <div className="w-full space-y-3 text-center">
              <p className="text-sm text-brand-950">
                Se l'indirizzo è registrato, riceverai a breve un'email con il link di accesso.
              </p>
              {mutation.data.debug_link && (
                <a
                  href={mutation.data.debug_link}
                  className="block break-all rounded-md bg-brand-50 p-3 text-xs text-brand-700 underline"
                >
                  [dev] Apri magic link: {mutation.data.debug_link}
                </a>
              )}
              <Button variant="ghost" size="sm" onClick={() => mutation.reset()}>
                Usa un altro indirizzo
              </Button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="w-full space-y-3">
              <Input
                type="email"
                required
                autoFocus
                placeholder="nome.cognome@email.it"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <Button type="submit" className="w-full" disabled={mutation.isPending}>
                {mutation.isPending ? "Invio in corso…" : "Invia link di accesso"}
              </Button>
              {mutation.isError && (
                <p className="text-center text-sm text-tricolore-rosso">
                  Impossibile inviare il link. Riprova tra qualche istante.
                </p>
              )}
            </form>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
