import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";

export function ContentPage({ eyebrow, title }: { eyebrow?: string; title: string }) {
  return (
    <div className="min-h-screen bg-white">
      <SiteHeader />
      <section className="mx-auto max-w-6xl px-6 py-16">
        {eyebrow && (
          <p className="text-sm font-medium tracking-wide text-brand-600 uppercase">{eyebrow}</p>
        )}
        <h1 className="mt-2 text-3xl font-semibold text-brand-950">{title}</h1>
        <p className="mt-4 max-w-2xl text-sm text-brand-950/60">
          Contenuti in aggiornamento: questa pagina sarà popolata a breve.
        </p>
      </section>
      <SiteFooter />
    </div>
  );
}
