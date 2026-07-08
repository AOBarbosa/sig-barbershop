export interface Servico {
  id_servico: number;
  nome: string;
  ativo: boolean;
  preco: string | number;
  duracao_em_minutos: number;
  pontos_gerados: number;
}

export interface ServicoPayload {
  nome: string;
  ativo: boolean;
  preco: number;
  duracao_em_minutos: number;
  pontos_gerados: number;
}
