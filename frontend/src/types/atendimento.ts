import type { Servico } from "@/types/servico";

export type AtendimentoStatus =
  "AGENDADO" | "EM_EXECUCAO" | "CONCLUIDO" | "CANCELADO";

export interface Pessoa {
  id_pessoa: number;
  nome: string;
  cpf: string;
  email: string | null;
  data_nascimento: string | null;
  admin: boolean;
}

export interface Cliente {
  PESSOA_id_pessoa: number;
  preferencias: string | null;
  observacoes: string | null;
}

export interface Barbeiro {
  PESSOA_id_pessoa: number;
  apelido: string | null;
  comissao_percentual: string | null;
}

export interface Disponibilidade {
  id_disponibilidade: number;
  BARBEIRO_PESSOA_id_pessoa: number;
  dia_semana: string;
  hora_inicio: string;
  hora_fim: string;
  ativo: boolean;
}

export interface Atendimento {
  id_atendimento: number;
  CLIENTE_PESSOA_id_pessoa: number;
  BARBEIRO_PESSOA_id_pessoa: number;
  data_hora_inicio: string;
  data_hora_fim: string | null;
  status: AtendimentoStatus;
  valor_total: string;
  observacoes: string | null;
}

export interface AtendimentoServico {
  ATENDIMENTO_id_atendimento: number;
  SERVICO_id_servico: number;
  preco_cobrado: string;
}

export interface AtendimentoPayload {
  CLIENTE_PESSOA_id_pessoa: number;
  BARBEIRO_PESSOA_id_pessoa: number;
  data_hora_inicio: string;
  data_hora_fim?: string | null;
  status: AtendimentoStatus;
  observacoes: string | null;
}

export interface AtendimentoFormPayload extends AtendimentoPayload {
  servicoIds: number[];
}

export interface AtendimentoLookups {
  pessoas: Pessoa[];
  clientes: Cliente[];
  barbeiros: Barbeiro[];
  servicos: Servico[];
  atendimentos: Atendimento[];
}
