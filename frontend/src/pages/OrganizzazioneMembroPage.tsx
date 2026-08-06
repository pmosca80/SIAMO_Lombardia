import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import { Card } from "@/components/ui/Card";

export function OrganizzazioneMembroPage({
  ruolo,
  cognome,
  email,
  foto,
}: {
  ruolo: string;
  cognome: string;
  email: string;
  foto: string;
}) {
  return (
    <div className="min-h-screen bg-white">
      <SiteHeader />

      <section className="mx-auto max-w-3xl px-6 py-16">
        <p className="text-sm font-medium tracking-wide text-brand-600 uppercase">Organizzazione</p>
        <h1 className="mt-2 text-3xl font-semibold text-brand-950">{ruolo}</h1>

        <Card className="mt-8 overflow-hidden sm:flex sm:items-stretch">
          <img
            src={foto}
            alt={`${ruolo} - ${cognome}`}
            className="aspect-[4/5] w-full object-cover sm:w-56"
          />
          <div className="flex flex-col justify-center p-6">
            <a href={`mailto:${email}`} className="text-sm text-brand-600 underline">
              {email}
            </a>
          </div>
        </Card>
      </section>

      <SiteFooter />
    </div>
  );
}
