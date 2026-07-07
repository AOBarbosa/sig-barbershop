export type TipoMovimentacao = "acumulo" | "resgate";

export interface HistoricoPontos {
  id_historico: number;
  CLIENTE_id_cliente: number;
  pontos: number;
  tipo_movimentacao: TipoMovimentacao;
  descricao: string | null;
  data_movimentacao: string;
}

export interface SaldoPontos {
  CLIENTE_id_cliente: number;
  saldo: number;
}
