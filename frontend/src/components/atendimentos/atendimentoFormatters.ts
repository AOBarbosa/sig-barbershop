import type {
  AtendimentoLookups,
  AtendimentoStatus
} from "@/types/atendimento";

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

export function statusLabel(status: AtendimentoStatus) {
  const labels: Record<AtendimentoStatus, string> = {
    agendado: "Agendado",
    em_andamento: "Em andamento",
    concluido: "Concluído",
    cancelado: "Cancelado"
  };

  return labels[status];
}

export function pessoaNome(pessoaId: number, lookups?: AtendimentoLookups) {
  return (
    lookups?.pessoas.find((pessoa) => pessoa.id_pessoa === pessoaId)?.nome ??
    "Pessoa não encontrada"
  );
}

export function clienteNome(clienteId: number, lookups?: AtendimentoLookups) {
  const cliente = lookups?.clientes.find(
    (item) => item.id_cliente === clienteId
  );

  return cliente ? pessoaNome(cliente.PESSOA_id_pessoa, lookups) : "Cliente";
}

export function barbeiroNome(barbeiroId: number, lookups?: AtendimentoLookups) {
  const barbeiro = lookups?.barbeiros.find(
    (item) => item.id_barbeiro === barbeiroId
  );

  return barbeiro ? pessoaNome(barbeiro.PESSOA_id_pessoa, lookups) : "Barbeiro";
}
