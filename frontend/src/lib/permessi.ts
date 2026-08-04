import { useAuthStore } from "@/store/auth-store";
import type { RuoloUtente } from "@/types/api";

const RUOLI_GESTIONE: RuoloUtente[] = ["amministratore", "operatore"];

export function usePuoGestire(): boolean {
  const ruolo = useAuthStore((s) => s.claims?.ruolo);
  return Boolean(ruolo && RUOLI_GESTIONE.includes(ruolo));
}

export function useEAmministratore(): boolean {
  const ruolo = useAuthStore((s) => s.claims?.ruolo);
  return ruolo === "amministratore";
}
