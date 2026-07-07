"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createBarbeiroWithPessoa,
  getBarbeiroComPessoa,
  getBarbeirosComPessoas,
  updateBarbeiroWithPessoa
} from "@/services/barbeiroService";
import type { BarbeiroFormPayload } from "@/types/barbeiro";

const barbeirosQueryKey = ["barbeiros"];

export function useBarbeiros() {
  return useQuery({
    queryKey: barbeirosQueryKey,
    queryFn: getBarbeirosComPessoas
  });
}

export function useBarbeiroComPessoa(id: number) {
  return useQuery({
    queryKey: [...barbeirosQueryKey, id, "com-pessoa"],
    queryFn: () => getBarbeiroComPessoa(id),
    enabled: Number.isFinite(id)
  });
}

export function useCreateBarbeiro() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: BarbeiroFormPayload) =>
      createBarbeiroWithPessoa(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: barbeirosQueryKey });
      void queryClient.invalidateQueries({ queryKey: ["pessoas"] });
    }
  });
}

export function useUpdateBarbeiro(barbeiroId: number, pessoaId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: BarbeiroFormPayload) =>
      updateBarbeiroWithPessoa(barbeiroId, pessoaId, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: barbeirosQueryKey });
      void queryClient.invalidateQueries({ queryKey: ["pessoas", pessoaId] });
    }
  });
}
