import { Link, useSearchParams } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { resetPassword } from "@/api/auth";
import { resetPasswordSchema, type ResetPasswordForm } from "@/lib/schemas";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card, CardBody } from "@/components/ui/Card";
import logo from "@/assets/logo.jpg";
import sfondo from "@/assets/sfondo.jpg";

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetPasswordForm>({ resolver: zodResolver(resetPasswordSchema) });

  const mutation = useMutation({
    mutationFn: (dati: ResetPasswordForm) => resetPassword(token ?? "", dati.password),
  });

  return (
    <div
      className="flex min-h-screen items-center justify-center bg-cover bg-center p-4"
      style={{ backgroundImage: `url(${sfondo})` }}
    >
      <Card className="w-full max-w-sm bg-white/95 backdrop-blur">
        <CardBody className="flex flex-col items-center gap-6">
          <img src={logo} alt="S.I.A.M.O. Esercito Lombardia" className="h-24 w-24" />
          <div className="text-center">
            <h1 className="text-lg font-semibold text-brand-950">Reimposta password</h1>
            <p className="text-sm text-brand-950/60">S.I.A.M.O. Esercito · Lombardia</p>
          </div>

          {!token ? (
            <p className="text-sm text-tricolore-rosso">Link non valido.</p>
          ) : mutation.isSuccess ? (
            <div className="w-full space-y-3 text-center">
              <p className="text-sm text-brand-950">{mutation.data.message}</p>
              <Link to="/login" className="inline-block text-sm text-brand-600 underline">
                Vai al login
              </Link>
            </div>
          ) : (
            <form
              onSubmit={handleSubmit((dati) => mutation.mutate(dati))}
              className="w-full space-y-3"
            >
              <div>
                <Input
                  type="password"
                  autoFocus
                  placeholder="Nuova password"
                  {...register("password")}
                />
                {errors.password && (
                  <p className="mt-1 text-xs text-tricolore-rosso">{errors.password.message}</p>
                )}
              </div>
              <div>
                <Input
                  type="password"
                  placeholder="Conferma nuova password"
                  {...register("confermaPassword")}
                />
                {errors.confermaPassword && (
                  <p className="mt-1 text-xs text-tricolore-rosso">
                    {errors.confermaPassword.message}
                  </p>
                )}
              </div>
              <Button type="submit" className="w-full" disabled={mutation.isPending}>
                {mutation.isPending ? "Aggiornamento…" : "Reimposta password"}
              </Button>
              {mutation.isError && (
                <p className="text-center text-sm text-tricolore-rosso">
                  Link non valido o scaduto. Richiedine uno nuovo.
                </p>
              )}
            </form>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
