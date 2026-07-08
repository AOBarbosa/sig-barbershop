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

export interface ClienteComPessoa extends Cliente {
  pessoa: Pessoa;
}

export interface PessoaPayload {
  nome: string;
  cpf: string;
  email: string | null;
  data_nascimento: string | null;
  admin?: boolean;
}

export type ClienteFormPayload = PessoaPayload;
