import type { AtendimentoSlot } from "@/components/atendimentos/atendimentoSlots";
import type { Disponibilidade } from "@/types/atendimento";
import type { BarbeiroComPessoa } from "@/types/barbeiro";

export interface HorarioOcupado {
  data_hora_inicio: string;
}

export interface AgendamentoCatalogo {
  barbeiros: BarbeiroComPessoa[];
}

export interface AgendamentoHorarios {
  disponibilidades: Disponibilidade[];
  horarios: AtendimentoSlot[];
}
