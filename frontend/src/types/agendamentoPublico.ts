import type { AtendimentoSlot } from "@/components/atendimentos/atendimentoSlots";
import type { Disponibilidade } from "@/types/atendimento";
import type { BarbeiroComPessoa } from "@/types/barbeiro";
import type { Servico } from "@/types/servico";

export interface HorarioOcupado {
  data_hora_inicio: string;
}

export interface AgendamentoCatalogo {
  barbeiros: BarbeiroComPessoa[];
  servicos: Servico[];
}

export interface AgendamentoHorarios {
  disponibilidades: Disponibilidade[];
  horarios: AtendimentoSlot[];
}
