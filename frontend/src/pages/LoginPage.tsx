import { Link, Navigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { login as loginRequest } from "@/api/auth";
import { loginSchema, type LoginForm } from "@/lib/schemas";
import { useAuthStore } from "@/store/auth-store";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card, CardBody } from "@/components/ui/Card";
import logo from "@/assets/logo.jpg";
import sfondo from "@/assets/sfondo.jpg";

export function LoginPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const setTokens = useAuthStore((s) => s.setTokens);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({ resolver: zodResolver(loginSchema) });

  const mutation = useMutation({
    mutationFn: (dati: LoginForm) => loginRequest(dati.email, dati.password),
    onSuccess: (coppia) => setTokens(coppia.access_token, coppia.refresh_token),
  });

  if (accessToken) {
    return <Navigate to="/" replace />;
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

          <form
            onSubmit={handleSubmit((dati) => mutation.mutate(dati))}
            className="w-full space-y-3"
          >
            <div>
              <Input
                type="email"
                autoFocus
                placeholder="nome.cognome@email.it"
                {...register("email")}
              />
              {errors.email && (
                <p className="mt-1 text-xs text-tricolore-rosso">{errors.email.message}</p>
              )}
            </div>
            <div>
              <Input type="password" placeholder="Password" {...register("password")} />
              {errors.password && (
                <p className="mt-1 text-xs text-tricolore-rosso">{errors.password.message}</p>
              )}
            </div>
            <Button type="submit" className="w-full" disabled={mutation.isPending}>
              {mutation.isPending ? "Accesso in corso…" : "Accedi"}
            </Button>
            {mutation.isError && (
              <p className="text-center text-sm text-tricolore-rosso">
                Email o password non corrette.
              </p>
            )}
          </form>

          <div className="flex w-full justify-between text-sm">
            <Link to="/password-dimenticata" className="text-brand-600 underline">
              Password dimenticata?
            </Link>
            <Link to="/registrati" className="text-brand-600 underline">
              Registrati
            </Link>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
