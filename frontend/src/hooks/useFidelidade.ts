"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createFidelidade,
  getFidelidade,
  getFidelidades,
  updateFidelidade
} from "@/services/fidelidadeService";
import { getProdutos } from "@/services/produtoService";
import { getServicos } from "@/services/servicoService";
import type { FidelidadePayload } from "@/types/fidelidade";

const fidelidadesQueryKey = ["fidelidades"];
const lookupsQueryKey = ["fidelidade-lookups"];

export function useFidelidades() {
  return useQuery({
    queryKey: fidelidadesQueryKey,
    queryFn: getFidelidades
  });
}

export function useFidelidadeItem(id: number) {
  return useQuery({
    queryKey: [...fidelidadesQueryKey, id],
    queryFn: () => getFidelidade(id),
    enabled: Number.isFinite(id)
  });
}

export function useFidelidadeLookups() {
  return useQuery({
    queryKey: lookupsQueryKey,
    queryFn: async () => {
      const [servicos, produtos] = await Promise.all([
        getServicos(),
        getProdutos()
      ]);

      return { servicos, produtos };
    }
  });
}

export function useCreateFidelidade() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createFidelidade,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: fidelidadesQueryKey });
    }
  });
}

export function useUpdateFidelidade(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: FidelidadePayload) => updateFidelidade(id, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: fidelidadesQueryKey });
      void queryClient.invalidateQueries({
        queryKey: [...fidelidadesQueryKey, id]
      });
    }
  });
}
