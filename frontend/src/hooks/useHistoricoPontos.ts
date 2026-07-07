"use client";

import { useQuery } from "@tanstack/react-query";

import {
  getHistoricoPontos,
  getSaldoPontos
} from "@/services/historicoPontosService";

export function useSaldoPontos(clienteId: number) {
  return useQuery({
    queryKey: ["clientes", clienteId, "pontos"],
    queryFn: () => getSaldoPontos(clienteId),
    enabled: Number.isFinite(clienteId)
  });
}

export function useHistoricoPontos(clienteId: number) {
  return useQuery({
    queryKey: ["clientes", clienteId, "pontos", "historico"],
    queryFn: () => getHistoricoPontos(clienteId),
    enabled: Number.isFinite(clienteId)
  });
}
