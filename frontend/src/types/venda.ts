export type VendaStatus = "ABERTA" | "PAGA" | "CANCELADA" | "ESTORNADA";

export type FormaPagamento =
  "DINHEIRO" | "CARTAO_DEBITO" | "CARTAO_CREDITO" | "PIX" | "OUTRO";

export interface Caixa {
  PESSOA_id_pessoa: number;
}

export interface Venda {
  id_venda: number;
  CLIENTE_PESSOA_id_pessoa: number;
  CAIXA_PESSOA_id_pessoa: number;
  data_hora: string;
  valor_total: string;
  status: VendaStatus;
  forma_pagamento: FormaPagamento;
  desconto: string;
}

export interface VendaProduto {
  VENDA_id_venda: number;
  PRODUTO_id_produto: number;
  quantidade: number;
  preco_unitario: string;
}

export interface VendaPayload {
  CLIENTE_PESSOA_id_pessoa: number;
  CAIXA_PESSOA_id_pessoa: number;
  data_hora: string;
  forma_pagamento: FormaPagamento;
  desconto?: number;
}

export interface VendaItemPayload {
  PRODUTO_id_produto: number;
  quantidade: number;
}

export interface VendaFormPayload extends VendaPayload {
  itens: VendaItemPayload[];
}
