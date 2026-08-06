import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import { Card, CardBody } from "@/components/ui/Card";
import { MEMBRI_ORGANIZZAZIONE } from "@/lib/organizzazione";

export function ContattiPage() {
  return (
    <div className="min-h-screen bg-white">
      <SiteHeader />

      <section className="mx-auto max-w-3xl px-6 py-16">
        <p className="text-sm font-medium tracking-wide text-brand-600 uppercase">
          S.I.A.M.O. Esercito Lombardia
        </p>
        <h1 className="mt-2 text-3xl font-semibold text-brand-950">Contatti</h1>

        <Card className="mt-8">
          <CardBody>
            <ul className="divide-y divide-silver-200">
              {MEMBRI_ORGANIZZAZIONE.map(({ ruolo, email }) => (
                <li key={ruolo} className="flex flex-col gap-1 py-4 sm:flex-row sm:items-center sm:gap-3">
                  <span className="font-medium text-brand-950">{ruolo}:</span>
                  <a href={`mailto:${email}`} className="text-brand-600 underline">
                    {email}
                  </a>
                </li>
              ))}
            </ul>
          </CardBody>
        </Card>
      </section>

      <SiteFooter />
    </div>
  );
}
