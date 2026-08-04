import { Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { passwordDimenticata } from "@/api/auth";
import { passwordDimenticataSchema, type PasswordDimenticataForm } from "@/lib/schemas";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card, CardBody } from "@/components/ui/Card";
import logo from "@/assets/logo.jpg";
import sfondo from "@/assets/sfondo.jpg";

export function ForgotPasswordPage() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PasswordDimenticataForm>({ resolver: zodResolver(passwordDimenticataSchema) });

  const mutation = useMutation({
    mutationFn: (dati: PasswordDimenticataForm) => passwordDimenticata(dati.email),
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
            <h1 className="text-lg font-semibold text-brand-950">Password dimenticata</h1>
            <p className="text-sm text-brand-950/60">S.I.A.M.O. Esercito · Lombardia</p>
          </div>

          {mutation.isSuccess ? (
            <div className="w-full space-y-3 text-center">
              <p className="text-sm text-brand-950">{mutation.data.message}</p>
              <Link to="/login" className="inline-block text-sm text-brand-600 underline">
                Torna al login
              </Link>
            </div>
          ) : (
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
              <Button type="submit" className="w-full" disabled={mutation.isPending}>
                {mutation.isPending ? "Invio in corso…" : "Invia link di reset"}
              </Button>
            </form>
          )}

          <Link to="/login" className="text-sm text-brand-600 underline">
            Torna al login
          </Link>
        </CardBody>
      </Card>
    </div>
  );
}
