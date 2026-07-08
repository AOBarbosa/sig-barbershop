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

export type BarbeiroFormPayload = PessoaPayload & BarbeiroPayload;
