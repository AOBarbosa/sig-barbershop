export interface Servico {
  id_servico: number;
  nome: string;
  descricao: string | null;
  preco: string;
  duracao_minutos: number;
  ativo: boolean;
}

export interface ServicoPayload {
  nome: string;
  descricao: string;
  preco: number;
  duracao_minutos: number;
  ativo: boolean;
}
