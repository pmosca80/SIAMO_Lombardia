import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { organizzazioneId } from "@/lib/config";
import type { Utente, UtenteCreate, UtenteUpdate } from "@/types/api";

const base = `/organizzazioni/${organizzazioneId}/utenti`;

export function useUtenti() {
  return useQuery({
    queryKey: ["utenti"],
    queryFn: async () => (await api.get<Utente[]>(base, { params: { limit: 200 } })).data,
  });
}

export function useUtente(id: number | null) {
  return useQuery({
    queryKey: ["utenti", id],
    queryFn: async () => (await api.get<Utente>(`${base}/${id}`)).data,
    enabled: id !== null,
  });
}

export function useCreaUtente() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (dati: UtenteCreate) => (await api.post<Utente>(base, dati)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["utenti"] }),
  });
}

export function useAggiornaUtente() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, dati }: { id: number; dati: UtenteUpdate }) =>
      (await api.patch<Utente>(`${base}/${id}`, dati)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["utenti"] }),
  });
}

export function useEliminaUtente() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`${base}/${id}`);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["utenti"] }),
  });
}
