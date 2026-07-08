"use client";

import { useQuery } from "@tanstack/react-query";

import {
  getCatalogoAgendamento,
  getHorariosAgendamento
} from "@/services/agendamentoPublicoService";

export function useCatalogoAgendamento() {
  return useQuery({
    queryKey: ["agendamento-publico", "catalogo"],
    queryFn: getCatalogoAgendamento
  });
}

export function useHorariosAgendamento(barbeiroId: number) {
  return useQuery({
    queryKey: ["agendamento-publico", "horarios", barbeiroId],
    queryFn: () => getHorariosAgendamento(barbeiroId),
    enabled: Number.isFinite(barbeiroId) && barbeiroId > 0
  });
}
