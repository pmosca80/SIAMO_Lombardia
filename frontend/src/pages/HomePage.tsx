import { ArrowRight, Clock } from "lucide-react";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import sfondo from "@/assets/sfondo.jpg";

const ISCRIZIONE_NAZIONALE_URL = "https://www.siamoesercito.org/iscrizioni";

const CTA_PRIMARY_MD =
  "inline-flex h-10 items-center justify-center gap-2 rounded-md bg-brand-600 px-4 text-sm font-medium text-white transition-colors hover:bg-brand-700";

export function HomePage() {
  return (
    <div className="min-h-screen bg-white">
      <SiteHeader />

      {/* Hero */}
      <section
        className="relative flex min-h-[420px] items-center bg-cover bg-center"
        style={{ backgroundImage: `url(${sfondo})` }}
      >
        <div className="absolute inset-0 bg-brand-950/75" />
        <div className="relative mx-auto max-w-6xl px-6 py-20">
          <p className="text-sm font-medium tracking-wide text-brand-100 uppercase">
            Sezione regionale Lombardia
          </p>
          <h1 className="mt-3 max-w-2xl text-4xl font-semibold text-white text-balance">
            Un punto di riferimento per il personale dell'Esercito in Lombardia
          </h1>
          <p className="mt-4 max-w-xl text-brand-100">
            Tutela, assistenza e comunicazione tra iscritti: tutto quello che offre
            S.I.A.M.O. Esercito, a livello regionale.
          </p>
          <div className="mt-5 inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-2 text-sm font-medium text-white ring-1 ring-white/25">
            <Clock size={16} />
            Assistenza 24 ore su 24
          </div>
          <div className="mt-8">
            <a
              href={ISCRIZIONE_NAZIONALE_URL}
              target="_blank"
              rel="noopener noreferrer"
              className={CTA_PRIMARY_MD}
            >
              Iscriviti al S.I.A.M.O. Esercito <ArrowRight size={16} />
            </a>
          </div>
        </div>
      </section>

      <SiteFooter />
    </div>
  );
}
