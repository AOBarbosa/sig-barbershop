import type { Pessoa, PessoaPayload } from "@/types/cliente";

export interface Barbeiro {
  PESSOA_id_pessoa: number;
  apelido: string | null;
  comissao_percentual: string | null;
}

export interface BarbeiroComPessoa extends Barbeiro {
  pessoa: Pessoa;
}

export interface BarbeiroPayload {
  apelido: string | null;
  comissao_percentual: number | null;
}

export interface DisponibilidadePayload {
  BARBEIRO_PESSOA_id_pessoa: number;
  dia_semana: string;
  hora_inicio: string;
  hora_fim: string;
}

export interface BarbeiroDisponibilidadePayload {
  dia_semana: string;
  hora_inicio: string;
  hora_fim: string;
}

export type BarbeiroFormPayload = PessoaPayload &
  BarbeiroPayload & {
    disponibilidades: BarbeiroDisponibilidadePayload[];
  };
