"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createServico,
  getServico,
  getServicos,
  updateServico
} from "@/services/servicoService";
import type { ServicoPayload } from "@/types/servico";

const servicosQueryKey = ["servicos"];

export function useServicos() {
  return useQuery({
    queryKey: servicosQueryKey,
    queryFn: getServicos
  });
}

export function useServico(id: number) {
  return useQuery({
    queryKey: [...servicosQueryKey, id],
    queryFn: () => getServico(id),
    enabled: Number.isFinite(id)
  });
}

export function useCreateServico() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createServico,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: servicosQueryKey });
    }
  });
}

export function useUpdateServico(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ServicoPayload) => updateServico(id, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: servicosQueryKey });
      void queryClient.invalidateQueries({
        queryKey: [...servicosQueryKey, id]
      });
    }
  });
}
