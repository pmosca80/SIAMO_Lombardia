import { Link } from "react-router-dom";
import { ArrowRight, Clock, Gift, HeartHandshake, Landmark, Scale } from "lucide-react";
import { Card, CardBody } from "@/components/ui/Card";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import sfondo from "@/assets/sfondo.jpg";

const ISCRIZIONE_NAZIONALE_URL = "https://www.siamoesercito.org/iscrizioni";

const CTA_PRIMARY_MD =
  "inline-flex h-10 items-center justify-center gap-2 rounded-md bg-brand-600 px-4 text-sm font-medium text-white transition-colors hover:bg-brand-700";

const COMUNICATI = [
  { data: "02.08.2026", titolo: "Assemblea regionale soci: convocazione e ordine del giorno" },
  { data: "30.07.2026", titolo: "Aggiornamento convenzione sanitaria, provincia di Milano" },
  { data: "28.07.2026", titolo: "Nuova sede della segreteria provinciale di Bergamo" },
  { data: "25.07.2026", titolo: "Contributi per l'edilizia popolare: modalità di richiesta" },
  { data: "21.07.2026", titolo: "Calendario incontri informativi sul territorio lombardo" },
];

const NORMATIVE = [
  { data: "31.07.2026", titolo: "Decreto interministeriale n. 45/2026" },
  { data: "26.07.2026", titolo: "Circolare Ministero della Difesa 12/2026" },
  { data: "19.07.2026", titolo: "Direttiva su trattamento economico accessorio" },
];

const SERVIZI = [
  {
    icona: Scale,
    titolo: "Tutela Legale",
    testo: "Assistenza legale dedicata agli iscritti, in convenzione con studi specializzati.",
  },
  {
    icona: Landmark,
    titolo: "Assistenza Fiscale",
    testo: "Supporto per dichiarazioni dei redditi, CAF e pratiche fiscali.",
  },
  {
    icona: HeartHandshake,
    titolo: "Sportello Psicologico",
    testo: "Un canale di ascolto riservato, gratuito per gli iscritti e i loro familiari.",
  },
  {
    icona: Gift,
    titolo: "Convenzioni e Vantaggi",
    testo: "Sconti e vantaggi presso partner convenzionati su tutto il territorio regionale.",
  },
];

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

      {/* Articolo in evidenza */}
      <section className="mx-auto max-w-6xl px-6 py-14">
        <Card className="border-l-4 border-l-brand-600">
          <CardBody>
            <p className="text-xs font-medium tracking-wide text-brand-950/50 uppercase">
              In evidenza · 04.08.2026
            </p>
            <h2 className="mt-2 text-xl font-semibold text-brand-950 text-balance">
              Edilizia popolare, in Lombardia via libera ai nuovi bandi
            </h2>
            <p className="mt-2 max-w-3xl text-sm text-brand-950/70">
              La Regione ha pubblicato i nuovi bandi per l'accesso all'edilizia popolare
              riservati al personale delle Forze Armate: i dettagli sui requisiti e sulle
              scadenze saranno diffusi ai soci tramite comunicazione ufficiale.
            </p>
          </CardBody>
        </Card>
      </section>

      {/* Comunicati */}
      <section id="comunicati" className="bg-silver-100 py-14">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="text-xl font-semibold text-brand-950">Ultimi comunicati</h2>
          <Card className="mt-6">
            <ul className="divide-y divide-silver-200">
              {COMUNICATI.map((c) => (
                <li key={c.titolo} className="flex items-center gap-4 px-5 py-3.5">
                  <span className="w-24 shrink-0 text-xs font-medium text-brand-950/50 tabular-nums">
                    {c.data}
                  </span>
                  <span className="text-sm text-brand-950">{c.titolo}</span>
                </li>
              ))}
            </ul>
          </Card>
        </div>
      </section>

      {/* Servizi per iscritti */}
      <section id="servizi" className="mx-auto max-w-6xl px-6 py-14">
        <h2 className="text-xl font-semibold text-brand-950">Servizi per iscritti</h2>
        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {SERVIZI.map(({ icona: Icona, titolo, testo }) => (
            <Card key={titolo}>
              <CardBody>
                <div className="flex h-10 w-10 items-center justify-center rounded-md bg-brand-50 text-brand-600">
                  <Icona size={20} />
                </div>
                <h3 className="mt-4 font-medium text-brand-950">{titolo}</h3>
                <p className="mt-1.5 text-sm text-brand-950/60">{testo}</p>
              </CardBody>
            </Card>
          ))}
        </div>
        <div className="mt-8 flex justify-center">
          <Link to="/registrati" className={CTA_PRIMARY_MD}>
            Registrati <ArrowRight size={16} />
          </Link>
        </div>
      </section>

      {/* Normative */}
      <section id="normative" className="bg-silver-100 py-14">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="text-xl font-semibold text-brand-950">Normative recenti</h2>
          <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
            {NORMATIVE.map((n) => (
              <Card key={n.titolo}>
                <CardBody>
                  <p className="text-xs font-medium text-brand-950/50 tabular-nums">{n.data}</p>
                  <p className="mt-2 text-sm font-medium text-brand-950 text-balance">{n.titolo}</p>
                </CardBody>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <SiteFooter />
    </div>
  );
}
