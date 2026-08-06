import { useState } from "react";
import { Link } from "react-router-dom";
import { Share2 } from "lucide-react";
import logo from "@/assets/logo.jpg";

const FACEBOOK_URL = "https://www.facebook.com/profile.php?id=61570740062439";

function FacebookIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className="h-4 w-4" aria-hidden="true">
      <path d="M22 12.06C22 6.505 17.523 2 12 2S2 6.505 2 12.06c0 5.02 3.657 9.184 8.438 9.94v-7.03H7.898v-2.91h2.54V9.845c0-2.526 1.492-3.922 3.777-3.922 1.094 0 2.238.197 2.238.197v2.476h-1.26c-1.243 0-1.63.775-1.63 1.57v1.888h2.773l-.443 2.91h-2.33V22c4.78-.756 8.437-4.92 8.437-9.94Z" />
    </svg>
  );
}

async function condividiPagina() {
  const dati = {
    title: "S.I.A.M.O. Esercito Lombardia",
    text: "Sezione regionale Lombardia di S.I.A.M.O. Esercito",
    url: window.location.href,
  };
  if (navigator.share) {
    await navigator.share(dati).catch(() => undefined);
    return true;
  }
  await navigator.clipboard.writeText(dati.url);
  return false;
}

export function SiteFooter() {
  const [linkCopiato, setLinkCopiato] = useState(false);

  async function handleCondividi() {
    const condiviso = await condividiPagina();
    if (!condiviso) {
      setLinkCopiato(true);
      setTimeout(() => setLinkCopiato(false), 2500);
    }
  }

  return (
    <footer className="bg-brand-950 text-white">
      <div className="mx-auto grid max-w-6xl grid-cols-1 gap-8 px-6 py-12 sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <div className="flex items-center gap-2">
            <img src={logo} alt="" className="h-8 w-8 rounded-full" />
            <span className="font-semibold">S.I.A.M.O. Esercito Lombardia</span>
          </div>
          <p className="mt-3 max-w-xs text-sm text-white/60">
            Sezione regionale di S.I.A.M.O. Esercito: tutela, assistenza e comunicazione
            per il personale dell'Esercito in Lombardia.
          </p>
        </div>
        <div>
          <p className="text-xs font-medium tracking-wide text-white/50 uppercase">Link utili</p>
          <ul className="mt-3 space-y-2 text-sm">
            <li>
              <Link to="/registrati" className="text-white/80 hover:text-white">
                Registrati
              </Link>
            </li>
            <li>
              <Link to="/login" className="text-white/80 hover:text-white">
                Area Personale
              </Link>
            </li>
            <li>
              <a
                href="https://www.siamoesercito.org/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-white/80 hover:text-white"
              >
                Sito nazionale ↗
              </a>
            </li>
          </ul>
        </div>
        <div>
          <p className="text-xs font-medium tracking-wide text-white/50 uppercase">Affiliazione</p>
          <p className="mt-3 text-sm text-white/60">Ministero della Difesa</p>
        </div>
        <div>
          <p className="text-xs font-medium tracking-wide text-white/50 uppercase">Seguici</p>
          <ul className="mt-3 space-y-2 text-sm">
            <li>
              <a
                href={FACEBOOK_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-white/80 hover:text-white"
              >
                <FacebookIcon />
                Facebook
              </a>
            </li>
            <li>
              <button
                type="button"
                onClick={handleCondividi}
                className="flex items-center gap-2 text-white/80 hover:text-white"
              >
                <Share2 size={16} />
                Condividi
              </button>
              {linkCopiato && <p className="mt-1 text-xs text-white/50">Link copiato negli appunti</p>}
            </li>
          </ul>
        </div>
      </div>
      <div className="border-t border-white/10 px-6 py-4 text-center text-xs text-white/50">
        © {new Date().getFullYear()} S.I.A.M.O. Esercito Lombardia
      </div>
    </footer>
  );
}
