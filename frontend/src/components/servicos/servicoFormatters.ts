import type { Servico } from "@/types/servico";

const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL"
});

export function formatCurrency(value: string | number) {
  return currencyFormatter.format(Number(value));
}

export function getAveragePrice(servicos: Servico[]) {
  if (servicos.length === 0) {
    return "0";
  }

  const total = servicos.reduce(
    (sum, servico) => sum + Number(servico.preco),
    0
  );
  return String(total / servicos.length);
}
