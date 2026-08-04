import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Plus, Send, Trash2 } from "lucide-react";
import {
  useComunicazioni,
  useCreaComunicazione,
  useEliminaComunicazione,
  useInviaComunicazione,
} from "@/api/comunicazioni";
import { usePuoGestire } from "@/lib/permessi";
import { comunicazioneCreateSchema, type ComunicazioneCreateForm } from "@/lib/schemas";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";

const CANALE_LABEL: Record<string, string> = { email: "Email", sms: "SMS", avviso: "Avviso in bacheca" };

export function ComunicazioniPage() {
  const { data: comunicazioni, isLoading } = useComunicazioni();
  const puoGestire = usePuoGestire();
  const creaComunicazione = useCreaComunicazione();
  const inviaComunicazione = useInviaComunicazione();
  const eliminaComunicazione = useEliminaComunicazione();
  const [formAperto, setFormAperto] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ComunicazioneCreateForm>({
    resolver: zodResolver(comunicazioneCreateSchema),
    defaultValues: { canale: "email" },
  });

  async function onSubmit(dati: ComunicazioneCreateForm) {
    await creaComunicazione.mutateAsync(dati);
    reset({ titolo: "", corpo: "", canale: "email" });
    setFormAperto(false);
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-brand-950">Comunicazioni</h1>
        {puoGestire && (
          <Button size="sm" onClick={() => setFormAperto((v) => !v)}>
            <Plus size={16} /> Nuova comunicazione
          </Button>
        )}
      </div>

      {formAperto && (
        <Card>
          <CardHeader className="font-medium text-brand-950">Nuova comunicazione</CardHeader>
          <CardBody>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
              <div>
                <Input placeholder="Titolo" {...register("titolo")} />
                {errors.titolo && (
                  <p className="mt-1 text-xs text-tricolore-rosso">{errors.titolo.message}</p>
                )}
              </div>
              <div>
                <textarea
                  placeholder="Testo della comunicazione"
                  rows={4}
                  className="w-full rounded-md border border-silver-300 bg-white p-3 text-sm text-brand-950 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
                  {...register("corpo")}
                />
                {errors.corpo && <p className="mt-1 text-xs text-tricolore-rosso">{errors.corpo.message}</p>}
              </div>
              <select
                className="h-10 rounded-md border border-silver-300 bg-white px-2 text-sm text-brand-950"
                {...register("canale")}
              >
                <option value="email">Email</option>
                <option value="sms">SMS</option>
                <option value="avviso">Avviso in bacheca</option>
              </select>
              <Button type="submit" size="sm" disabled={creaComunicazione.isPending}>
                {creaComunicazione.isPending ? "Salvataggio…" : "Salva come bozza"}
              </Button>
            </form>
          </CardBody>
        </Card>
      )}

      <div className="space-y-3">
        {isLoading && <p className="text-sm text-brand-950/50">Caricamento…</p>}
        {comunicazioni?.map((c) => (
          <Card key={c.id}>
            <CardBody className="flex items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-medium text-brand-950">{c.titolo}</h3>
                  <Badge variant={c.stato === "inviata" ? "success" : "neutral"}>
                    {c.stato === "inviata" ? "Inviata" : "Bozza"}
                  </Badge>
                  <Badge variant="brand">{CANALE_LABEL[c.canale]}</Badge>
                </div>
                <p className="mt-1 whitespace-pre-wrap text-sm text-brand-950/70">{c.corpo}</p>
              </div>
              {puoGestire && (
                <div className="flex shrink-0 gap-2">
                  {c.stato === "bozza" && (
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => inviaComunicazione.mutate(c.id)}
                      disabled={inviaComunicazione.isPending}
                    >
                      <Send size={14} /> Invia
                    </Button>
                  )}
                  {c.stato === "bozza" && (
                    <button
                      type="button"
                      title="Elimina"
                      onClick={() => {
                        if (confirm(`Eliminare la bozza "${c.titolo}"?`)) {
                          eliminaComunicazione.mutate(c.id);
                        }
                      }}
                      className="text-brand-950/40 hover:text-tricolore-rosso"
                    >
                      <Trash2 size={16} />
                    </button>
                  )}
                </div>
              )}
            </CardBody>
          </Card>
        ))}
        {comunicazioni?.length === 0 && (
          <p className="text-sm text-brand-950/50">Nessuna comunicazione ancora.</p>
        )}
      </div>
    </div>
  );
}
