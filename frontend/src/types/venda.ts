export type VendaStatus = "pendente" | "concluida" | "cancelada";

export type FormaPagamento =
  "dinheiro" | "cartao_debito" | "cartao_credito" | "pix";

export interface Caixa {
  id_caixa: number;
  PESSOA_id_pessoa: number;
}

export interface Venda {
  id_venda: number;
  CLIENTE_id_cliente: number;
  CAIXA_id_caixa: number;
  data_venda: string;
  valor_total: string;
  status: VendaStatus;
  forma_pagamento: FormaPagamento | null;
}

export interface VendaProduto {
  id_venda_produto: number;
  VENDA_id_venda: number;
  PRODUTO_id_produto: number;
  quantidade: number;
  preco_unitario: string;
}

export interface VendaPayload {
  CLIENTE_id_cliente: number;
  CAIXA_id_caixa: number;
  forma_pagamento: FormaPagamento | null;
}

export interface VendaItemPayload {
  PRODUTO_id_produto: number;
  quantidade: number;
}

export interface VendaFormPayload extends VendaPayload {
  itens: VendaItemPayload[];
}
