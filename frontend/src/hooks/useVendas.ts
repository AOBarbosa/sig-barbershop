"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { getClientes, getPessoas } from "@/services/clienteService";
import { getProdutos } from "@/services/produtoService";
import {
  createVendaWithProdutos,
  getCaixas,
  getVenda,
  getVendaProdutos,
  getVendas,
  updateVendaStatus
} from "@/services/vendaService";
import type { VendaFormPayload, VendaStatus } from "@/types/venda";

const vendasQueryKey = ["vendas"];
const lookupsQueryKey = ["vendas-lookups"];

export function useVendas() {
  return useQuery({
    queryKey: vendasQueryKey,
    queryFn: getVendas
  });
}

export function useVenda(id: number) {
  return useQuery({
    queryKey: [...vendasQueryKey, id],
    queryFn: () => getVenda(id),
    enabled: Number.isFinite(id)
  });
}

export function useVendaProdutos(id: number) {
  return useQuery({
    queryKey: [...vendasQueryKey, id, "produtos"],
    queryFn: () => getVendaProdutos(id),
    enabled: Number.isFinite(id)
  });
}

export function useVendaLookups() {
  return useQuery({
    queryKey: lookupsQueryKey,
    queryFn: async () => {
      const [pessoas, clientes, caixas, produtos] = await Promise.all([
        getPessoas(),
        getClientes(),
        getCaixas(),
        getProdutos()
      ]);

      return { pessoas, clientes, caixas, produtos };
    }
  });
}

export function useCreateVenda() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: VendaFormPayload) => createVendaWithProdutos(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: vendasQueryKey,
        exact: true
      });
    }
  });
}

export function useUpdateVendaStatus(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (status: VendaStatus) => updateVendaStatus(id, status),
    onSuccess: (venda) => {
      queryClient.setQueryData([...vendasQueryKey, id], venda);
      void queryClient.invalidateQueries({
        queryKey: vendasQueryKey,
        exact: true
      });
    }
  });
}
