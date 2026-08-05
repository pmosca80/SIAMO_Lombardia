import { z } from "zod";

export const registrazioneSchema = z
  .object({
    nome: z.string().min(1, "Obbligatorio").max(120),
    cognome: z.string().min(1, "Obbligatorio").max(120),
    email: z.email("Email non valida"),
    numeroTessera: z.string().min(1, "Obbligatorio").max(50),
    password: z.string().min(8, "Almeno 8 caratteri"),
    confermaPassword: z.string().min(1, "Obbligatorio"),
  })
  .refine((dati) => dati.password === dati.confermaPassword, {
    message: "Le password non coincidono",
    path: ["confermaPassword"],
  });
export type RegistrazioneForm = z.infer<typeof registrazioneSchema>;

export const loginSchema = z.object({
  email: z.email("Email non valida"),
  password: z.string().min(1, "Obbligatorio"),
});
export type LoginForm = z.infer<typeof loginSchema>;

export const passwordDimenticataSchema = z.object({
  email: z.email("Email non valida"),
});
export type PasswordDimenticataForm = z.infer<typeof passwordDimenticataSchema>;

export const resetPasswordSchema = z
  .object({
    password: z.string().min(8, "Almeno 8 caratteri"),
    confermaPassword: z.string().min(1, "Obbligatorio"),
  })
  .refine((dati) => dati.password === dati.confermaPassword, {
    message: "Le password non coincidono",
    path: ["confermaPassword"],
  });
export type ResetPasswordForm = z.infer<typeof resetPasswordSchema>;

export const utenteCreateSchema = z.object({
  nome: z.string().min(1, "Obbligatorio").max(120),
  cognome: z.string().min(1, "Obbligatorio").max(120),
  email: z.email("Email non valida"),
  numeroTessera: z.string().max(50).optional(),
  ruolo: z.enum(["amministratore", "operatore", "socio"]),
});
export type UtenteCreateForm = z.infer<typeof utenteCreateSchema>;

export const comunicazioneCreateSchema = z.object({
  titolo: z.string().min(1, "Obbligatorio").max(255),
  corpo: z.string().min(1, "Obbligatorio"),
  canale: z.enum(["email", "sms", "avviso"]),
});
export type ComunicazioneCreateForm = z.infer<typeof comunicazioneCreateSchema>;
