import { Link } from "react-router-dom";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import { Button } from "@/components/ui/Button";
import { segretarioEmail } from "@/lib/config";

export function ConsulenzaGratuitaPage() {
  return (
    <div className="min-h-screen bg-white">
      <SiteHeader />

      <section className="mx-auto max-w-6xl px-6 py-16">
        <div className="grid grid-cols-1 gap-10 lg:grid-cols-[1.4fr_1fr]">
          <div>
            <p className="text-sm font-medium tracking-wide text-brand-600 uppercase">
              Servizi e Ticket
            </p>
            <h1 className="mt-2 text-3xl font-semibold text-brand-950">Hai bisogno di aiuto?</h1>
            <h2 className="mt-1 text-2xl font-semibold text-brand-950">Scrivici!</h2>

            <p className="mt-6 max-w-xl text-sm text-brand-950/70">
              I nostri esperti sono a disposizione di tutto il personale dell'Esercito Italiano
              iscritto in Lombardia.
            </p>
            <p className="mt-3 max-w-xl text-sm text-brand-950/70">
              Invia una mail di informazioni all'indirizzo{" "}
              <a href={`mailto:${segretarioEmail}`} className="font-medium text-brand-600 underline">
                {segretarioEmail}
              </a>
              .
            </p>
            <p className="mt-3 max-w-xl text-sm text-brand-950/70">
              Sarai ricontattato dal nostro servizio di consulenza.
            </p>
          </div>

          <div className="rounded-lg border border-silver-200 bg-silver-100 p-6">
            <h3 className="text-xl font-semibold text-brand-950">
              Vuoi aderire al S.I.A.M.O. Esercito?
            </h3>
            <p className="mt-3 text-sm text-brand-950/60">
              Iscriviti all'associazione e accedi ai servizi dedicati agli iscritti.
            </p>
            <div className="mt-6 flex flex-col gap-3">
              <Link to="/registrati">
                <Button className="w-full">Iscriviti ora</Button>
              </Link>
              <Link to="/login">
                <Button variant="secondary" className="w-full">
                  Sei già iscritto? Entra nella tua area riservata
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      <SiteFooter />
    </div>
  );
}
