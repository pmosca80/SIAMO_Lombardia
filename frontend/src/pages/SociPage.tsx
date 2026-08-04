import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Plus, Trash2 } from "lucide-react";
import { useAggiornaUtente, useCreaUtente, useEliminaUtente, useUtenti } from "@/api/utenti";
import { usePuoGestire, useEAmministratore } from "@/lib/permessi";
import { utenteCreateSchema, type UtenteCreateForm } from "@/lib/schemas";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { RuoloBadge } from "@/components/RuoloBadge";
import type { RuoloUtente } from "@/types/api";

export function SociPage() {
  const { data: soci, isLoading } = useUtenti();
  const puoGestire = usePuoGestire();
  const eAmministratore = useEAmministratore();
  const creaUtente = useCreaUtente();
  const aggiornaUtente = useAggiornaUtente();
  const eliminaUtente = useEliminaUtente();
  const [formAperto, setFormAperto] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<UtenteCreateForm>({
    resolver: zodResolver(utenteCreateSchema),
    defaultValues: { ruolo: "socio" },
  });

  async function onSubmit(dati: UtenteCreateForm) {
    await creaUtente.mutateAsync({ ...dati, attivo: true });
    reset({ nome: "", cognome: "", email: "", ruolo: "socio" });
    setFormAperto(false);
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-brand-950">Soci</h1>
        {puoGestire && (
          <Button size="sm" onClick={() => setFormAperto((v) => !v)}>
            <Plus size={16} /> Nuovo socio
          </Button>
        )}
      </div>

      {formAperto && (
        <Card>
          <CardHeader className="font-medium text-brand-950">Nuovo socio</CardHeader>
          <CardBody>
            <form onSubmit={handleSubmit(onSubmit)} className="grid grid-cols-1 gap-3 sm:grid-cols-4">
              <div>
                <Input placeholder="Nome" {...register("nome")} />
                {errors.nome && <p className="mt-1 text-xs text-tricolore-rosso">{errors.nome.message}</p>}
              </div>
              <div>
                <Input placeholder="Cognome" {...register("cognome")} />
                {errors.cognome && (
                  <p className="mt-1 text-xs text-tricolore-rosso">{errors.cognome.message}</p>
                )}
              </div>
              <div>
                <Input placeholder="Email" type="email" {...register("email")} />
                {errors.email && <p className="mt-1 text-xs text-tricolore-rosso">{errors.email.message}</p>}
              </div>
              <select
                className="h-10 rounded-md border border-silver-300 bg-white px-2 text-sm text-brand-950"
                {...register("ruolo")}
              >
                <option value="socio">Socio</option>
                <option value="operatore">Operatore</option>
                {eAmministratore && <option value="amministratore">Amministratore</option>}
              </select>
              <div className="sm:col-span-4">
                <Button type="submit" size="sm" disabled={creaUtente.isPending}>
                  {creaUtente.isPending ? "Salvataggio…" : "Crea socio"}
                </Button>
              </div>
            </form>
          </CardBody>
        </Card>
      )}

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-silver-200 text-brand-950/60">
              <tr>
                <th className="px-4 py-3 font-medium">Nome</th>
                <th className="px-4 py-3 font-medium">Email</th>
                <th className="px-4 py-3 font-medium">Ruolo</th>
                <th className="px-4 py-3 font-medium">Stato</th>
                {puoGestire && <th className="px-4 py-3" />}
              </tr>
            </thead>
            <tbody>
              {isLoading && (
                <tr>
                  <td className="px-4 py-4 text-brand-950/50" colSpan={5}>
                    Caricamento…
                  </td>
                </tr>
              )}
              {soci?.map((u) => (
                <tr key={u.id} className="border-b border-silver-100 last:border-0">
                  <td className="px-4 py-3 text-brand-950">
                    {u.nome} {u.cognome}
                  </td>
                  <td className="px-4 py-3 text-brand-950/70">{u.email}</td>
                  <td className="px-4 py-3">
                    {puoGestire ? (
                      <select
                        className="rounded-md border border-silver-300 bg-white px-2 py-1 text-sm"
                        value={u.ruolo}
                        onChange={(e) =>
                          aggiornaUtente.mutate({
                            id: u.id,
                            dati: { ruolo: e.target.value as RuoloUtente },
                          })
                        }
                      >
                        <option value="socio">Socio</option>
                        <option value="operatore">Operatore</option>
                        {eAmministratore && <option value="amministratore">Amministratore</option>}
                      </select>
                    ) : (
                      <RuoloBadge ruolo={u.ruolo} />
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {puoGestire ? (
                      <button
                        type="button"
                        onClick={() =>
                          aggiornaUtente.mutate({ id: u.id, dati: { attivo: !u.attivo } })
                        }
                        className={
                          u.attivo
                            ? "rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-tricolore-verde"
                            : "rounded-full bg-silver-200 px-2.5 py-0.5 text-xs font-medium text-brand-950/60"
                        }
                      >
                        {u.attivo ? "Attivo" : "Disattivato"}
                      </button>
                    ) : (
                      <span>{u.attivo ? "Attivo" : "Disattivato"}</span>
                    )}
                  </td>
                  {puoGestire && (
                    <td className="px-4 py-3 text-right">
                      {eAmministratore && (
                        <button
                          type="button"
                          title="Elimina"
                          onClick={() => {
                            if (confirm(`Eliminare ${u.nome} ${u.cognome}?`)) {
                              eliminaUtente.mutate(u.id);
                            }
                          }}
                          className="text-brand-950/40 hover:text-tricolore-rosso"
                        >
                          <Trash2 size={16} />
                        </button>
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
