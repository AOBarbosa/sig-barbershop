import type { Atendimento, Disponibilidade } from "@/types/atendimento";

const diaSemanaMap: Record<number, string> = {
  0: "DOMINGO",
  1: "SEGUNDA",
  2: "TERCA",
  3: "QUARTA",
  4: "QUINTA",
  5: "SEXTA",
  6: "SABADO"
};

export interface AtendimentoSlot {
  value: string;
  label: string;
}

function pad(value: number) {
  return String(value).padStart(2, "0");
}

function toInputValue(date: Date) {
  const year = date.getFullYear();
  const month = pad(date.getMonth() + 1);
  const day = pad(date.getDate());
  const hour = pad(date.getHours());
  const minute = pad(date.getMinutes());
  return `${year}-${month}-${day}T${hour}:${minute}`;
}

function toLabel(date: Date) {
  const day = pad(date.getDate());
  const month = pad(date.getMonth() + 1);
  const year = date.getFullYear();
  const hour = pad(date.getHours());
  const minute = pad(date.getMinutes());
  return `${day}/${month}/${year} ${hour}:${minute}`;
}

function setTime(date: Date, time: string) {
  const [hours, minutes] = time.split(":").map(Number);
  const next = new Date(date);
  next.setHours(hours, minutes, 0, 0);
  return next;
}

function horariosOcupados(atendimentos: Atendimento[], barbeiroId: number) {
  return new Set(
    atendimentos
      .filter((item) => item.BARBEIRO_PESSOA_id_pessoa === barbeiroId)
      .filter((item) => item.status !== "CANCELADO")
      .map((item) => item.data_hora_inicio.slice(0, 16))
  );
}

export function gerarHorariosDisponiveis({
  barbeiroId,
  disponibilidades,
  atendimentos
}: {
  barbeiroId: number;
  disponibilidades: Disponibilidade[];
  atendimentos: Atendimento[];
}): AtendimentoSlot[] {
  const ocupados = horariosOcupados(atendimentos, barbeiroId);
  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);

  return Array.from({ length: 14 }).flatMap((_, index) => {
    const dia = new Date(hoje);
    dia.setDate(hoje.getDate() + index);
    const disponibilidade = disponibilidades.find(
      (item) => item.dia_semana === diaSemanaMap[dia.getDay()] && item.ativo
    );

    if (!disponibilidade) {
      return [];
    }

    const inicio = setTime(dia, disponibilidade.hora_inicio);
    const fim = setTime(dia, disponibilidade.hora_fim);
    const slots: AtendimentoSlot[] = [];

    for (
      let slot = inicio;
      slot < fim;
      slot = new Date(slot.getTime() + 30 * 60000)
    ) {
      const value = toInputValue(slot);
      if (!ocupados.has(value)) {
        slots.push({ value, label: toLabel(slot) });
      }
    }

    return slots;
  });
}
