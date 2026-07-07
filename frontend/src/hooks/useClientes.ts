"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createClienteWithPessoa,
  getCliente,
  getClientesComPessoas,
  getPessoa,
  updatePessoa
} from "@/services/clienteService";
import type { ClienteFormPayload, PessoaPayload } from "@/types/cliente";

const clientesQueryKey = ["clientes"];

export function useClientes() {
  return useQuery({
    queryKey: clientesQueryKey,
    queryFn: getClientesComPessoas
  });
}

export function useCliente(id: number) {
  return useQuery({
    queryKey: [...clientesQueryKey, id],
    queryFn: () => getCliente(id),
    enabled: Number.isFinite(id)
  });
}

export function usePessoaDoCliente(pessoaId: number | undefined) {
  return useQuery({
    queryKey: ["pessoas", pessoaId],
    queryFn: () => getPessoa(pessoaId as number),
    enabled: Number.isFinite(pessoaId)
  });
}

export function useCreateCliente() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ClienteFormPayload) =>
      createClienteWithPessoa(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: clientesQueryKey });
      void queryClient.invalidateQueries({ queryKey: ["pessoas"] });
    }
  });
}

export function useUpdateClientePessoa(pessoaId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: PessoaPayload) => updatePessoa(pessoaId, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: clientesQueryKey });
      void queryClient.invalidateQueries({ queryKey: ["pessoas", pessoaId] });
    }
  });
}
