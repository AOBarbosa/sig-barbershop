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

export interface ClienteComPessoa extends Cliente {
  pessoa: Pessoa;
}

export interface PessoaPayload {
  nome: string;
  cpf: string;
  email: string | null;
  data_nascimento: string | null;
}

export interface ClienteFormPayload extends PessoaPayload {}
