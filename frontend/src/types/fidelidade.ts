export interface Fidelidade {
  id_fidelidade: number;
  SERVICO_id_servico: number | null;
  PRODUTO_id_produto: number | null;
  pontos: number;
  ativo: boolean;
}

export interface FidelidadePayload {
  SERVICO_id_servico: number | null;
  PRODUTO_id_produto: number | null;
  pontos: number;
  ativo: boolean;
}
