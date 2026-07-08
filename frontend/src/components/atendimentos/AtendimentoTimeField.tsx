"use client";

import { AtendimentoFieldError } from "@/components/atendimentos/AtendimentoFieldError";
import type { AtendimentoSlot } from "@/components/atendimentos/atendimentoSlots";

export function AtendimentoTimeField({
  error,
  loading,
  barbeiroId,
  horarios,
  register
}: {
  error?: string;
  loading: boolean;
  barbeiroId: number;
  horarios: AtendimentoSlot[];
  register: object;
}) {
  return (
    <AtendimentoFieldError message={error}>
      <label className="text-sm font-medium" htmlFor="data_hora_inicio">
        Horário disponível
      </label>
      <select
        id="data_hora_inicio"
        className="h-10 rounded-lg border px-3 text-sm"
        {...register}
        name="data_hora_inicio"
        disabled={!barbeiroId || loading}>
        <option value="">Selecione</option>
        {horarios.map((horario) => (
          <option key={horario.value} value={horario.value}>
            {horario.label}
          </option>
        ))}
      </select>
    </AtendimentoFieldError>
  );
}
