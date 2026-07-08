"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createBarbeiroWithPessoa,
  getDisponibilidadesDoBarbeiro,
  getBarbeiroComPessoa,
  getBarbeirosComPessoas,
  saveBarbeiroDisponibilidade,
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
    queryFn: async () => {
      const [barbeiro, disponibilidades] = await Promise.all([
        getBarbeiroComPessoa(id),
        getDisponibilidadesDoBarbeiro(id)
      ]);

      return { ...barbeiro, disponibilidade: disponibilidades[0] };
    },
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
    mutationFn: async (payload: BarbeiroFormPayload) => {
      const barbeiro = await updateBarbeiroWithPessoa(barbeiroId, payload);
      await saveBarbeiroDisponibilidade(barbeiroId, {
        dia_semana: payload.dia_semana,
        hora_inicio: payload.hora_inicio,
        hora_fim: payload.hora_fim
      });
      return barbeiro;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: barbeirosQueryKey });
      void queryClient.invalidateQueries({ queryKey: ["pessoas", pessoaId] });
    }
  });
}
