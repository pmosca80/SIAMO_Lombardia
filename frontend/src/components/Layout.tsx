import type { ReactNode } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { LayoutDashboard, LogOut, Megaphone, Users } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/store/auth-store";
import { useUtente } from "@/api/utenti";
import { logout as logoutRequest } from "@/api/auth";
import { RuoloBadge } from "@/components/RuoloBadge";
import logo from "@/assets/logo.jpg";

const NAV = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/soci", label: "Soci", icon: Users, end: false },
  { to: "/comunicazioni", label: "Comunicazioni", icon: Megaphone, end: false },
];

export function Layout({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  const claims = useAuthStore((s) => s.claims);
  const refreshToken = useAuthStore((s) => s.refreshToken);
  const clear = useAuthStore((s) => s.clear);
  const { data: utente } = useUtente(claims?.utente_id ?? null);

  async function handleLogout() {
    if (refreshToken) {
      await logoutRequest(refreshToken).catch(() => undefined);
    }
    clear();
    navigate("/login", { replace: true });
  }

  return (
    <div className="flex min-h-screen bg-silver-100">
      <aside className="flex w-60 shrink-0 flex-col bg-brand-950 text-white">
        <div className="flex items-center gap-2 px-5 py-5">
          <img src={logo} alt="" className="h-10 w-10 rounded-full" />
          <div className="leading-tight">
            <p className="text-sm font-semibold">S.I.A.M.O.</p>
            <p className="text-xs text-white/60">Esercito Lombardia</p>
          </div>
        </div>
        <nav className="flex flex-1 flex-col gap-1 px-3 py-2">
          {NAV.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-white/80 hover:bg-white/10 hover:text-white",
                  isActive && "bg-white/15 text-white",
                )
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-silver-200 bg-white px-6 py-3">
          <div />
          <div className="flex items-center gap-3">
            {utente && (
              <div className="flex items-center gap-2 text-sm">
                <span className="text-brand-950">
                  {utente.nome} {utente.cognome}
                </span>
                <RuoloBadge ruolo={utente.ruolo} />
              </div>
            )}
            <button
              type="button"
              onClick={handleLogout}
              className="flex items-center gap-1 rounded-md px-2 py-1.5 text-sm text-brand-950/60 hover:bg-silver-100 hover:text-brand-950"
              title="Esci"
            >
              <LogOut size={16} />
            </button>
          </div>
        </header>
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
