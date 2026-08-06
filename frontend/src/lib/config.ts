export const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

// Questo frontend serve un solo tenant (SIAMO Lombardia): l'organizzazione_id
// è fisso e non richiesto all'utente in fase di login.
export const organizzazioneId = Number(import.meta.env.VITE_ORGANIZZAZIONE_ID ?? "1");

export const segretarioEmail = "segretariolombardia@siamoesercito.it";
