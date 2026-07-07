"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createProduto,
  getProduto,
  getProdutos,
  updateProduto
} from "@/services/produtoService";
import type { ProdutoPayload } from "@/types/produto";

const produtosQueryKey = ["produtos"];

export function useProdutos() {
  return useQuery({
    queryKey: produtosQueryKey,
    queryFn: getProdutos
  });
}

export function useProduto(id: number) {
  return useQuery({
    queryKey: [...produtosQueryKey, id],
    queryFn: () => getProduto(id),
    enabled: Number.isFinite(id)
  });
}

export function useCreateProduto() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createProduto,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: produtosQueryKey });
    }
  });
}

export function useUpdateProduto(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ProdutoPayload) => updateProduto(id, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: produtosQueryKey });
      void queryClient.invalidateQueries({
        queryKey: [...produtosQueryKey, id]
      });
    }
  });
}
