import type { Servico } from "@/types/servico";

export type AtendimentoStatus =
  "agendado" | "em_andamento" | "concluido" | "cancelado";

export interface Pessoa {
  id_pessoa: number;
  nome: string;
  cpf: string;
  email: string | null;
  data_nascimento: string | null;
  created_at: string;
  updated_at: string;
}

export interface Cliente {
  id_cliente: number;
  PESSOA_id_pessoa: number;
}

export interface Barbeiro {
  id_barbeiro: number;
  PESSOA_id_pessoa: number;
  especialidade: string | null;
  ativo: boolean;
}

export interface Disponibilidade {
  id_disponibilidade: number;
  BARBEIRO_id_barbeiro: number;
  dia_semana: string;
  hora_inicio: string;
  hora_fim: string;
}

export interface Atendimento {
  id_atendimento: number;
  CLIENTE_id_cliente: number;
  BARBEIRO_id_barbeiro: number;
  data_hora: string;
  status: AtendimentoStatus;
  valor_total: string;
  observacao: string | null;
}

export interface AtendimentoServico {
  id_atendimento_servico: number;
  ATENDIMENTO_id_atendimento: number;
  SERVICO_id_servico: number;
  preco_cobrado: string;
}

export interface AtendimentoPayload {
  CLIENTE_id_cliente: number;
  BARBEIRO_id_barbeiro: number;
  data_hora: string;
  status: AtendimentoStatus;
  observacao: string | null;
}

export interface AtendimentoFormPayload extends AtendimentoPayload {
  servicoIds: number[];
}

export interface AtendimentoLookups {
  pessoas: Pessoa[];
  clientes: Cliente[];
  barbeiros: Barbeiro[];
  servicos: Servico[];
}
