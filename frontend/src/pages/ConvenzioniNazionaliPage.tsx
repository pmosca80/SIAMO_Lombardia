import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import { Card, CardBody } from "@/components/ui/Card";
import { CATEGORIE_CONVENZIONI_NAZIONALI } from "@/lib/convenzioni";

export function ConvenzioniNazionaliPage() {
  return (
    <div className="min-h-screen bg-white">
      <SiteHeader />

      <section className="mx-auto max-w-3xl px-6 py-16">
        <p className="text-sm font-medium tracking-wide text-brand-600 uppercase">Convenzioni</p>
        <h1 className="mt-2 text-3xl font-semibold text-brand-950">Convenzioni Nazionali</h1>
        <p className="mt-4 text-sm text-brand-950/60">
          Categorie in aggiornamento: le convenzioni attive saranno pubblicate a breve.
        </p>

        <Card className="mt-8">
          <CardBody>
            <ul className="grid grid-cols-1 gap-x-8 sm:grid-cols-2">
              {CATEGORIE_CONVENZIONI_NAZIONALI.map((categoria) => (
                <li key={categoria} className="border-b border-silver-200 py-3 text-sm text-brand-950">
                  {categoria}
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
