import { Link } from "react-router-dom";
import { LayoutDashboard, LogIn } from "lucide-react";
import { useAuthStore } from "@/store/auth-store";
import { NavDropdown } from "@/components/NavDropdown";
import logo from "@/assets/logo.jpg";

const CTA_PRIMARY_SM =
  "inline-flex h-8 items-center justify-center gap-2 rounded-md bg-brand-600 px-3 text-sm font-medium text-white transition-colors hover:bg-brand-700";

export function SiteHeader() {
  const accessToken = useAuthStore((s) => s.accessToken);

  return (
    <header className="sticky top-0 z-10 border-b border-silver-200 bg-white/95 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-6 px-6 py-3">
        <Link to="/" className="flex items-center gap-2">
          <img src={logo} alt="S.I.A.M.O. Esercito Lombardia" className="h-9 w-9 rounded-full" />
          <span className="text-sm font-semibold text-brand-950">S.I.A.M.O. Esercito Lombardia</span>
        </Link>

        <nav className="hidden items-center gap-6 text-sm font-medium text-brand-950/70 md:flex">
          <Link to="/" className="hover:text-brand-950">
            Home
          </Link>
          <NavDropdown
            label="Organizzazione"
            items={[
              { label: "Presidente", to: "/organizzazione/presidente" },
              { label: "Segretario", to: "/organizzazione/segretario" },
              { label: "Vice Segretario", to: "/organizzazione/vice-segretario" },
            ]}
          />
          <Link to="/normative" className="hover:text-brand-950">
            Normative
          </Link>
          <NavDropdown
            label="Convenzioni"
            items={[
              { label: "Convenzioni Nazionali", to: "/convenzioni/nazionali" },
              { label: "Convenzioni Locali", to: "/convenzioni/locali" },
            ]}
          />
          <NavDropdown
            label="Servizi"
            items={[
              { label: "Tutela Legale", to: "/servizi/tutela-legale" },
              { label: "Assistenza Fiscale", to: "/servizi/assistenza-fiscale" },
              { label: "Pronto PSY", to: "/servizi/pronto-psy" },
              { label: "Corporate Benefit", to: "/servizi/corporate-benefit" },
            ]}
          />
        </nav>

        <div className="flex items-center gap-3">
          {accessToken ? (
            <Link
              to="/dashboard"
              className="flex items-center gap-1.5 text-sm font-medium text-brand-700 hover:text-brand-900"
            >
              <LayoutDashboard size={16} /> Dashboard
            </Link>
          ) : (
            <Link
              to="/login"
              className="flex items-center gap-1.5 text-sm font-medium text-brand-700 hover:text-brand-900"
            >
              <LogIn size={16} /> Area Personale
            </Link>
          )}
          <Link to="/registrati" className={CTA_PRIMARY_SM}>
            Registrati
          </Link>
        </div>
      </div>
    </header>
  );
}
