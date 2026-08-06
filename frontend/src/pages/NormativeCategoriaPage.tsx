import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import { Card, CardBody } from "@/components/ui/Card";
import type { CategoriaNormativa } from "@/lib/normative";

export function NormativeCategoriaPage({ nome, argomenti }: CategoriaNormativa) {
  return (
    <div className="min-h-screen bg-white">
      <SiteHeader />

      <section className="mx-auto max-w-3xl px-6 py-16">
        <p className="text-sm font-medium tracking-wide text-brand-600 uppercase">Normative</p>
        <h1 className="mt-2 text-3xl font-semibold text-brand-950">{nome}</h1>
        <p className="mt-4 text-sm text-brand-950/60">
          Argomenti in aggiornamento: i documenti saranno pubblicati a breve.
        </p>

        <Card className="mt-8">
          <CardBody>
            <ul className="divide-y divide-silver-200">
              {argomenti.map((argomento) => (
                <li key={argomento} className="py-3 text-sm text-brand-950">
                  {argomento}
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
