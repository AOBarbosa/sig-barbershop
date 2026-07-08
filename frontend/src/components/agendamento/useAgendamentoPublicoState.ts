"use client";

import { useState } from "react";

import {
  useCatalogoAgendamento,
  useHorariosAgendamento
} from "@/hooks/useAgendamentoPublico";

export function useAgendamentoPublicoState(
  initialBarbeiro: number,
  initialHorario: string
) {
  const [barbeiroId, setBarbeiroId] = useState(initialBarbeiro);
  const [horario, setHorario] = useState(initialHorario);
  const catalogoQuery = useCatalogoAgendamento();
  const horariosQuery = useHorariosAgendamento(barbeiroId);

  return {
    barbeiroId,
    barbeiros: catalogoQuery.data?.barbeiros ?? [],
    horario,
    horarios: horariosQuery.data?.horarios ?? [],
    selectBarbeiro: (id: number) => {
      setBarbeiroId(id);
      setHorario("");
    },
    selectHorario: setHorario,
    setBarbeiroId,
    setHorario
  };
}
