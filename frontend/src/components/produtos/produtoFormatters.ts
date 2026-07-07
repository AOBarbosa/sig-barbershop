import type { Produto } from "@/types/produto";

const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL"
});

export function formatCurrency(value: string | number) {
  return currencyFormatter.format(Number(value));
}

export function getAveragePrice(produtos: Produto[]) {
  if (produtos.length === 0) {
    return "0";
  }

  const total = produtos.reduce(
    (sum, produto) => sum + Number(produto.preco),
    0
  );
  return String(total / produtos.length);
}

export function getEstoqueValue(produtos: Produto[]) {
  const total = produtos.reduce(
    (sum, produto) => sum + Number(produto.preco) * produto.estoque,
    0
  );
  return String(total);
}
