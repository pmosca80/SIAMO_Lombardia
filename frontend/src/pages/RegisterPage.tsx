import { Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { registrati } from "@/api/auth";
import { registrazioneSchema, type RegistrazioneForm } from "@/lib/schemas";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card, CardBody } from "@/components/ui/Card";
import logo from "@/assets/logo.jpg";
import sfondo from "@/assets/sfondo.jpg";

export function RegisterPage() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegistrazioneForm>({ resolver: zodResolver(registrazioneSchema) });

  const mutation = useMutation({
    mutationFn: (dati: RegistrazioneForm) =>
      registrati({
        nome: dati.nome,
        cognome: dati.cognome,
        email: dati.email,
        password: dati.password,
      }),
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
            <h1 className="text-lg font-semibold text-brand-950">Registrati</h1>
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
                <Input placeholder="Nome" autoFocus {...register("nome")} />
                {errors.nome && (
                  <p className="mt-1 text-xs text-tricolore-rosso">{errors.nome.message}</p>
                )}
              </div>
              <div>
                <Input placeholder="Cognome" {...register("cognome")} />
                {errors.cognome && (
                  <p className="mt-1 text-xs text-tricolore-rosso">{errors.cognome.message}</p>
                )}
              </div>
              <div>
                <Input type="email" placeholder="nome.cognome@email.it" {...register("email")} />
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
              <div>
                <Input
                  type="password"
                  placeholder="Conferma password"
                  {...register("confermaPassword")}
                />
                {errors.confermaPassword && (
                  <p className="mt-1 text-xs text-tricolore-rosso">
                    {errors.confermaPassword.message}
                  </p>
                )}
              </div>
              <Button type="submit" className="w-full" disabled={mutation.isPending}>
                {mutation.isPending ? "Registrazione in corso…" : "Registrati"}
              </Button>
              {mutation.isError && (
                <p className="text-center text-sm text-tricolore-rosso">
                  Impossibile completare la registrazione. Riprova tra qualche istante.
                </p>
              )}
            </form>
          )}

          <Link to="/login" className="text-sm text-brand-600 underline">
            Hai già un account? Accedi
          </Link>
        </CardBody>
      </Card>
    </div>
  );
}
