export type RuoloUtente = "amministratore" | "operatore" | "socio";

export type CanaleComunicazione = "email" | "sms" | "avviso";
export type StatoComunicazione = "bozza" | "inviata";

export interface Utente {
  id: number;
  organizzazione_id: number;
  nome: string;
  cognome: string;
  email: string;
  ruolo: RuoloUtente;
  attivo: boolean;
  created_at: string;
  updated_at: string;
}

export interface UtenteCreate {
  nome: string;
  cognome: string;
  email: string;
  ruolo: RuoloUtente;
  attivo: boolean;
}

export interface UtenteUpdate {
  nome?: string;
  cognome?: string;
  ruolo?: RuoloUtente;
  attivo?: boolean;
}

export interface Comunicazione {
  id: number;
  organizzazione_id: number;
  titolo: string;
  corpo: string;
  canale: CanaleComunicazione;
  stato: StatoComunicazione;
  campagna_id: number | null;
  autore_id: number | null;
  inviata_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ComunicazioneCreate {
  titolo: string;
  corpo: string;
  canale: CanaleComunicazione;
  campagna_id?: number | null;
  autore_id?: number | null;
}

export interface ComunicazioneUpdate {
  titolo?: string;
  corpo?: string;
  canale?: CanaleComunicazione;
  campagna_id?: number | null;
  autore_id?: number | null;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface MagicLinkRequestRead {
  message: string;
  debug_link: string | null;
}
