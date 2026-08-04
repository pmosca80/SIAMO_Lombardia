import type { RuoloUtente } from "@/types/api";

export interface AccessTokenClaims {
  utente_id: number;
  organizzazione_id: number;
  ruolo: RuoloUtente;
  exp: number;
}

/**
 * Decodifica il payload di un access token JWT senza verificarne la firma:
 * la firma è verificata dal backend ad ogni richiesta, qui serve solo a
 * leggere `sub`/`org`/`ruolo` per popolare la UI senza una chiamata /me
 * (che l'API non espone).
 */
export function decodeAccessToken(token: string): AccessTokenClaims | null {
  try {
    const [, payload] = token.split(".");
    const json = JSON.parse(atob(payload.replace(/-/g, "+").replace(/_/g, "/")));
    return {
      utente_id: Number(json.sub),
      organizzazione_id: Number(json.org),
      ruolo: json.ruolo as RuoloUtente,
      exp: Number(json.exp),
    };
  } catch {
    return null;
  }
}

export function isExpired(exp: number): boolean {
  return Date.now() >= exp * 1000;
}
