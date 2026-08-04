import { z } from "zod";

export const utenteCreateSchema = z.object({
  nome: z.string().min(1, "Obbligatorio").max(120),
  cognome: z.string().min(1, "Obbligatorio").max(120),
  email: z.email("Email non valida"),
  ruolo: z.enum(["amministratore", "operatore", "socio"]),
});
export type UtenteCreateForm = z.infer<typeof utenteCreateSchema>;

export const comunicazioneCreateSchema = z.object({
  titolo: z.string().min(1, "Obbligatorio").max(255),
  corpo: z.string().min(1, "Obbligatorio"),
  canale: z.enum(["email", "sms", "avviso"]),
});
export type ComunicazioneCreateForm = z.infer<typeof comunicazioneCreateSchema>;
