"use client";

import { useState } from "react";

import {
  useCatalogoAgendamento,
  useHorariosAgendamento
} from "@/hooks/useAgendamentoPublico";

export function useAgendamentoPublicoState(
  initialBarbeiro: number,
  initialHorario: string,
  initialServicoIds: number[] = []
) {
  const [barbeiroId, setBarbeiroId] = useState(initialBarbeiro);
  const [horario, setHorario] = useState(initialHorario);
  const [servicoIds, setServicoIds] = useState(initialServicoIds);
  const catalogoQuery = useCatalogoAgendamento();
  const horariosQuery = useHorariosAgendamento(barbeiroId);

  return {
    barbeiroId,
    barbeiros: catalogoQuery.data?.barbeiros ?? [],
    horario,
    horarios: horariosQuery.data?.horarios ?? [],
    servicoIds,
    servicos: catalogoQuery.data?.servicos ?? [],
    selectBarbeiro: (id: number) => {
      setBarbeiroId(id);
      setHorario("");
    },
    selectHorario: setHorario,
    toggleServico: (id: number) => {
      setServicoIds((current) =>
        current.includes(id)
          ? current.filter((servicoId) => servicoId !== id)
          : [...current, id]
      );
    },
    setBarbeiroId,
    setHorario,
    setServicoIds
  };
}
