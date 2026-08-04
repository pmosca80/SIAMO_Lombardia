import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { organizzazioneId } from "@/lib/config";
import type { Comunicazione, ComunicazioneCreate, ComunicazioneUpdate } from "@/types/api";

const base = `/organizzazioni/${organizzazioneId}/comunicazioni`;

export function useComunicazioni() {
  return useQuery({
    queryKey: ["comunicazioni"],
    queryFn: async () =>
      (await api.get<Comunicazione[]>(base, { params: { limit: 200 } })).data,
  });
}

export function useCreaComunicazione() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (dati: ComunicazioneCreate) =>
      (await api.post<Comunicazione>(base, dati)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["comunicazioni"] }),
  });
}

export function useAggiornaComunicazione() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, dati }: { id: number; dati: ComunicazioneUpdate }) =>
      (await api.patch<Comunicazione>(`${base}/${id}`, dati)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["comunicazioni"] }),
  });
}

export function useInviaComunicazione() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) =>
      (await api.post<Comunicazione>(`${base}/${id}/invia`)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["comunicazioni"] }),
  });
}

export function useEliminaComunicazione() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`${base}/${id}`);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["comunicazioni"] }),
  });
}
