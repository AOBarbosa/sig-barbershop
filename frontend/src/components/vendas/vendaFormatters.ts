import type { Cliente, Pessoa } from "@/types/cliente";
import type { Caixa, FormaPagamento, VendaStatus } from "@/types/venda";

export const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL"
});

export function formatCurrency(value: string | number) {
  return currencyFormatter.format(Number(value));
}

export function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short"
  }).format(new Date(value));
}

export function statusLabel(status: VendaStatus) {
  const labels: Record<VendaStatus, string> = {
    ABERTA: "Pendente",
    PAGA: "Concluída",
    CANCELADA: "Cancelada",
    ESTORNADA: "Estornada"
  };

  return labels[status];
}

export function formaPagamentoLabel(forma: FormaPagamento | null) {
  const labels: Record<FormaPagamento, string> = {
    DINHEIRO: "Dinheiro",
    CARTAO_DEBITO: "Cartão de débito",
    CARTAO_CREDITO: "Cartão de crédito",
    PIX: "Pix",
    OUTRO: "Outro"
  };

  return forma ? labels[forma] : "Não informada";
}

export interface VendaLookups {
  pessoas: Pessoa[];
  clientes: Cliente[];
  caixas: Caixa[];
}

export function pessoaNome(pessoaId: number, lookups?: VendaLookups) {
  return (
    lookups?.pessoas.find((pessoa) => pessoa.id_pessoa === pessoaId)?.nome ??
    "Pessoa não encontrada"
  );
}

export function clienteNome(clienteId: number, lookups?: VendaLookups) {
  const cliente = lookups?.clientes.find(
    (item) => item.PESSOA_id_pessoa === clienteId
  );

  return cliente ? pessoaNome(cliente.PESSOA_id_pessoa, lookups) : "Cliente";
}

export function caixaLabel(caixaId: number, lookups?: VendaLookups) {
  const caixa = lookups?.caixas.find(
    (item) => item.PESSOA_id_pessoa === caixaId
  );

  return caixa
    ? `Caixa de ${pessoaNome(caixa.PESSOA_id_pessoa, lookups)}`
    : "Caixa";
}
