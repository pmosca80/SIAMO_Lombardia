import { Link } from "react-router-dom";
import logo from "@/assets/logo.jpg";

export function SiteFooter() {
  return (
    <footer className="bg-brand-950 text-white">
      <div className="mx-auto grid max-w-6xl grid-cols-1 gap-8 px-6 py-12 sm:grid-cols-3">
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
      </div>
      <div className="border-t border-white/10 px-6 py-4 text-center text-xs text-white/50">
        © {new Date().getFullYear()} S.I.A.M.O. Esercito Lombardia
      </div>
    </footer>
  );
}
