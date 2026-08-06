import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import { Card, CardBody } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Textarea } from "@/components/ui/Textarea";
import { Button } from "@/components/ui/Button";
import { ticketSchema, TICKET_CATEGORIE, type TicketForm } from "@/lib/schemas";
import { segretarioEmail } from "@/lib/config";

function buildMailto(dati: TicketForm) {
  const oggetto = `Ticket S.I.A.M.O. Esercito Lombardia – ${dati.categoria}`;
  const corpo = [
    `Nome e cognome: ${dati.nomeCognome}`,
    dati.numeroTessera ? `Numero tessera: ${dati.numeroTessera}` : null,
    dati.telefono ? `Numero di telefono: ${dati.telefono}` : null,
    `E-mail: ${dati.email}`,
    `Categoria: ${dati.categoria}`,
    "",
    "Messaggio:",
    dati.messaggio,
  ]
    .filter((riga) => riga !== null)
    .join("\n");

  return `mailto:${segretarioEmail}?subject=${encodeURIComponent(oggetto)}&body=${encodeURIComponent(corpo)}`;
}

export function ApriTicketPage() {
  const [inviato, setInviato] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TicketForm>({ resolver: zodResolver(ticketSchema) });

  function onSubmit(dati: TicketForm) {
    window.location.href = buildMailto(dati);
    setInviato(true);
  }

  return (
    <div className="min-h-screen bg-white">
      <SiteHeader />

      <section className="mx-auto max-w-3xl px-6 py-16">
        <p className="text-sm font-medium tracking-wide text-brand-600 uppercase">Servizi e Ticket</p>
        <h1 className="mt-2 text-3xl font-semibold text-brand-950">Apri il tuo ticket</h1>
        <p className="mt-4 text-sm text-brand-950/60">
          Compila il modulo: si aprirà il tuo programma di posta con la richiesta già pronta per
          essere inviata a <span className="font-medium text-brand-950">{segretarioEmail}</span>.
        </p>

        <Card className="mt-8">
          <CardBody>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="mb-1 block text-sm font-medium text-brand-950">
                    Nome e cognome
                  </label>
                  <Input placeholder="Mario Rossi" {...register("nomeCognome")} />
                  {errors.nomeCognome && (
                    <p className="mt-1 text-xs text-tricolore-rosso">{errors.nomeCognome.message}</p>
                  )}
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-brand-950">
                    Numero tessera
                  </label>
                  <Input placeholder="Facoltativo" {...register("numeroTessera")} />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-brand-950">
                    Numero di telefono
                  </label>
                  <Input placeholder="Facoltativo" {...register("telefono")} />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-brand-950">E-mail</label>
                  <Input type="email" placeholder="nome.cognome@email.it" {...register("email")} />
                  {errors.email && (
                    <p className="mt-1 text-xs text-tricolore-rosso">{errors.email.message}</p>
                  )}
                </div>
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-brand-950">
                  Seleziona una categoria
                </label>
                <Select defaultValue="" {...register("categoria")}>
                  <option value="" disabled>
                    Scegli una categoria
                  </option>
                  {TICKET_CATEGORIE.map((categoria) => (
                    <option key={categoria} value={categoria}>
                      {categoria}
                    </option>
                  ))}
                </Select>
                {errors.categoria && (
                  <p className="mt-1 text-xs text-tricolore-rosso">{errors.categoria.message}</p>
                )}
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-brand-950">Messaggio</label>
                <Textarea rows={5} placeholder="Descrivi la tua richiesta" {...register("messaggio")} />
                {errors.messaggio && (
                  <p className="mt-1 text-xs text-tricolore-rosso">{errors.messaggio.message}</p>
                )}
              </div>

              <Button type="submit" className="w-full sm:w-auto">
                Invia
              </Button>

              {inviato && (
                <p className="text-sm text-brand-700">
                  Si è aperto il tuo programma di posta con la richiesta precompilata: controlla e
                  invia l'email per completare l'apertura del ticket.
                </p>
              )}
            </form>
          </CardBody>
        </Card>
      </section>

      <SiteFooter />
    </div>
  );
}
