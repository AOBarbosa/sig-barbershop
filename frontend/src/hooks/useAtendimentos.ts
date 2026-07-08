"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { getServicos } from "@/services/servicoService";
import {
  createAtendimento,
  createAtendimentoWithServicos,
  getAtendimento,
  getAtendimentos,
  getAtendimentoServicos,
  getBarbeiros,
  getClientes,
  getDisponibilidadesDoBarbeiro,
  getPessoas,
  updateAtendimentoStatus
} from "@/services/atendimentoService";
import type {
  AtendimentoFormPayload,
  AtendimentoStatus
} from "@/types/atendimento";

const atendimentosQueryKey = ["atendimentos"];
const lookupsQueryKey = ["atendimentos-lookups"];

export function useAtendimentos() {
  return useQuery({
    queryKey: atendimentosQueryKey,
    queryFn: getAtendimentos
  });
}

export function useAtendimento(id: number) {
  return useQuery({
    queryKey: [...atendimentosQueryKey, id],
    queryFn: () => getAtendimento(id),
    enabled: Number.isFinite(id)
  });
}

export function useAtendimentoServicos(id: number) {
  return useQuery({
    queryKey: [...atendimentosQueryKey, id, "servicos"],
    queryFn: () => getAtendimentoServicos(id),
    enabled: Number.isFinite(id)
  });
}

export function useAtendimentoLookups() {
  return useQuery({
    queryKey: lookupsQueryKey,
    queryFn: async () => {
      const [pessoas, clientes, barbeiros, servicos, atendimentos] =
        await Promise.all([
          getPessoas(),
          getClientes(),
          getBarbeiros(),
          getServicos(),
          getAtendimentos()
        ]);

      return { pessoas, clientes, barbeiros, servicos, atendimentos };
    }
  });
}

export function useDisponibilidadesDoBarbeiro(barbeiroId: number) {
  return useQuery({
    queryKey: ["barbeiros", barbeiroId, "disponibilidades"],
    queryFn: () => getDisponibilidadesDoBarbeiro(barbeiroId),
    enabled: Number.isFinite(barbeiroId) && barbeiroId > 0
  });
}

export function useCreateAtendimento() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: AtendimentoFormPayload) =>
      createAtendimentoWithServicos(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: atendimentosQueryKey,
        exact: true
      });
    }
  });
}

export function useCreateAtendimentoCliente() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: AtendimentoFormPayload) =>
      createAtendimentoWithServicos(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: atendimentosQueryKey,
        exact: true
      });
    }
  });
}

export function useUpdateAtendimentoStatus(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (status: AtendimentoStatus) =>
      updateAtendimentoStatus(id, status),
    onSuccess: (atendimento) => {
      queryClient.setQueryData([...atendimentosQueryKey, id], atendimento);
      void queryClient.invalidateQueries({
        queryKey: atendimentosQueryKey,
        exact: true
      });
    }
  });
}
