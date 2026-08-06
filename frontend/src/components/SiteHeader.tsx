import { useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { LayoutDashboard, LogIn, Menu, X } from "lucide-react";
import { useAuthStore } from "@/store/auth-store";
import { NavDropdown } from "@/components/NavDropdown";
import logo from "@/assets/logo.jpg";

const CTA_PRIMARY_SM =
  "inline-flex h-8 items-center justify-center gap-2 rounded-md bg-brand-600 px-3 text-sm font-medium text-white transition-colors hover:bg-brand-700";

const ORGANIZZAZIONE_ITEMS = [
  { label: "Presidente", to: "/organizzazione/presidente" },
  { label: "Segretario", to: "/organizzazione/segretario" },
  { label: "Vice Segretario", to: "/organizzazione/vice-segretario" },
];

const CONVENZIONI_ITEMS = [
  { label: "Convenzioni Nazionali", to: "/convenzioni/nazionali" },
  { label: "Convenzioni Locali", to: "/convenzioni/locali" },
];

const SERVIZI_ITEMS = [
  { label: "Apri il tuo ticket", to: "/servizi/apri-ticket" },
  { label: "Ricevi una consulenza gratuita", to: "/servizi/consulenza-gratuita" },
  { label: "Tutela Legale", to: "/servizi/tutela-legale" },
  { label: "Assistenza Fiscale", to: "/servizi/assistenza-fiscale" },
  { label: "Pronto PSY", to: "/servizi/pronto-psy" },
  { label: "Corporate Benefit", to: "/servizi/corporate-benefit" },
];

export function SiteHeader() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const [mobileOpen, setMobileOpen] = useState(false);

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
          <NavDropdown label="Organizzazione" items={ORGANIZZAZIONE_ITEMS} />
          <Link to="/normative" className="hover:text-brand-950">
            Normative
          </Link>
          <NavDropdown label="Convenzioni" items={CONVENZIONI_ITEMS} />
          <NavDropdown label="Servizi e Ticket" items={SERVIZI_ITEMS} />
        </nav>

        <div className="flex items-center gap-3">
          <Link
            to="/contatti"
            className="hidden text-sm font-medium text-brand-950/70 hover:text-brand-950 md:block"
          >
            Contatti
          </Link>
          {accessToken ? (
            <Link
              to="/dashboard"
              className="hidden items-center gap-1.5 text-sm font-medium text-brand-700 hover:text-brand-900 sm:flex"
            >
              <LayoutDashboard size={16} /> Dashboard
            </Link>
          ) : (
            <Link
              to="/login"
              className="hidden items-center gap-1.5 text-sm font-medium text-brand-700 hover:text-brand-900 sm:flex"
            >
              <LogIn size={16} /> Area Personale
            </Link>
          )}
          <Link to="/registrati" className={CTA_PRIMARY_SM}>
            Registrati
          </Link>

          <button
            type="button"
            onClick={() => setMobileOpen((v) => !v)}
            aria-expanded={mobileOpen}
            aria-label="Apri il menu"
            className="flex h-8 w-8 items-center justify-center rounded-md text-brand-950 hover:bg-silver-100 md:hidden"
          >
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {mobileOpen && (
        <nav className="border-t border-silver-200 bg-white px-6 py-4 text-sm md:hidden">
          <MobileLink to="/" onNavigate={() => setMobileOpen(false)}>
            Home
          </MobileLink>

          <MobileGroup label="Organizzazione" items={ORGANIZZAZIONE_ITEMS} onNavigate={() => setMobileOpen(false)} />

          <MobileLink to="/normative" onNavigate={() => setMobileOpen(false)}>
            Normative
          </MobileLink>

          <MobileGroup label="Convenzioni" items={CONVENZIONI_ITEMS} onNavigate={() => setMobileOpen(false)} />
          <MobileGroup label="Servizi e Ticket" items={SERVIZI_ITEMS} onNavigate={() => setMobileOpen(false)} />

          <MobileLink to="/contatti" onNavigate={() => setMobileOpen(false)}>
            Contatti
          </MobileLink>
          <MobileLink to={accessToken ? "/dashboard" : "/login"} onNavigate={() => setMobileOpen(false)}>
            {accessToken ? "Dashboard" : "Area Personale"}
          </MobileLink>
        </nav>
      )}
    </header>
  );
}

function MobileLink({
  to,
  onNavigate,
  children,
}: {
  to: string;
  onNavigate: () => void;
  children: ReactNode;
}) {
  return (
    <Link
      to={to}
      onClick={onNavigate}
      className="block border-b border-silver-100 py-3 font-medium text-brand-950"
    >
      {children}
    </Link>
  );
}

function MobileGroup({
  label,
  items,
  onNavigate,
}: {
  label: string;
  items: { label: string; to: string }[];
  onNavigate: () => void;
}) {
  return (
    <div className="border-b border-silver-100 py-3">
      <p className="font-medium text-brand-950">{label}</p>
      <div className="mt-2 flex flex-col gap-2 pl-3">
        {items.map((item) => (
          <Link
            key={item.to}
            to={item.to}
            onClick={onNavigate}
            className="text-brand-950/70 hover:text-brand-950"
          >
            {item.label}
          </Link>
        ))}
      </div>
    </div>
  );
}
