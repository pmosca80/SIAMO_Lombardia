import { api } from "@/lib/api";
import { organizzazioneId } from "@/lib/config";
import type { MessaggioGenerico, TokenPair } from "@/types/api";

export async function registrati(dati: {
  nome: string;
  cognome: string;
  email: string;
  numeroTessera: string;
  password: string;
}): Promise<MessaggioGenerico> {
  const { data } = await api.post<MessaggioGenerico>("/auth/registrati", {
    organizzazione_id: organizzazioneId,
    nome: dati.nome,
    cognome: dati.cognome,
    email: dati.email,
    numero_tessera: dati.numeroTessera,
    password: dati.password,
  });
  return data;
}

export async function verificaEmail(token: string): Promise<TokenPair> {
  const { data } = await api.post<TokenPair>("/auth/verifica-email", null, {
    params: { token },
  });
  return data;
}

export async function login(email: string, password: string): Promise<TokenPair> {
  const { data } = await api.post<TokenPair>("/auth/login", {
    organizzazione_id: organizzazioneId,
    email,
    password,
  });
  return data;
}

export async function passwordDimenticata(email: string): Promise<MessaggioGenerico> {
  const { data } = await api.post<MessaggioGenerico>("/auth/password-dimenticata", {
    organizzazione_id: organizzazioneId,
    email,
  });
  return data;
}

export async function resetPassword(
  token: string,
  nuovaPassword: string,
): Promise<MessaggioGenerico> {
  const { data } = await api.post<MessaggioGenerico>("/auth/reset-password", {
    token,
    nuova_password: nuovaPassword,
  });
  return data;
}

export async function logout(refreshToken: string): Promise<void> {
  await api.post("/auth/logout", { refresh_token: refreshToken });
}
