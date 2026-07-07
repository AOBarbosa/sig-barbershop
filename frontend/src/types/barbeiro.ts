import type { Pessoa, PessoaPayload } from "@/types/cliente";

export interface Barbeiro {
  id_barbeiro: number;
  PESSOA_id_pessoa: number;
  especialidade: string | null;
  ativo: boolean;
}

export interface BarbeiroComPessoa extends Barbeiro {
  pessoa: Pessoa;
}

export interface BarbeiroPayload {
  especialidade: string | null;
  ativo: boolean;
}

export type BarbeiroFormPayload = PessoaPayload & BarbeiroPayload;
