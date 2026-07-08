export type TipoMovimentacao = "acumulo" | "resgate";

export interface HistoricoPontos {
  id_historico: number;
  CLIENTE_PESSOA_id_pessoa: number;
  pontos: number;
  tipo_movimentacao: TipoMovimentacao;
  descricao: string | null;
  data_movimentacao: string;
}

export interface SaldoPontos {
  CLIENTE_PESSOA_id_pessoa: number;
  saldo: number;
}
