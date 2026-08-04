import { api } from "@/lib/api";
import { organizzazioneId } from "@/lib/config";
import type { MagicLinkRequestRead, TokenPair } from "@/types/api";

export async function richiediMagicLink(email: string): Promise<MagicLinkRequestRead> {
  const { data } = await api.post<MagicLinkRequestRead>("/auth/magic-link", {
    organizzazione_id: organizzazioneId,
    email,
  });
  return data;
}

export async function verificaMagicLink(token: string): Promise<TokenPair> {
  const { data } = await api.post<TokenPair>("/auth/verify", { token });
  return data;
}

export async function logout(refreshToken: string): Promise<void> {
  await api.post("/auth/logout", { refresh_token: refreshToken });
}
