import type { Produto } from "@/types/produto";

export function getCategoriasCount(produtos: Produto[]) {
  const categorias = produtos
    .map((produto) => produto.categoria)
    .filter((categoria): categoria is string => Boolean(categoria));

  return new Set(categorias).size;
}

export function formatCurrency(value: string | number) {
  return Number(value).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL"
  });
}
