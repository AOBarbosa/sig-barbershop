import type { Produto } from "@/types/produto";
import type { Fidelidade } from "@/types/fidelidade";
import type { Servico } from "@/types/servico";

export function servicoNome(id: number | null, servicos: Servico[]) {
  return (
    servicos.find((servico) => servico.id_servico === id)?.nome ??
    "Serviço não encontrado"
  );
}

export function produtoNome(id: number | null, produtos: Produto[]) {
  return (
    produtos.find((produto) => produto.id_produto === id)?.nome ??
    "Produto não encontrado"
  );
}

export function origemLabel(fidelidade: Fidelidade) {
  return fidelidade.SERVICO_id_servico ? "Serviço" : "Produto";
}

export function origemNome(
  fidelidade: Fidelidade,
  servicos: Servico[],
  produtos: Produto[]
) {
  return fidelidade.SERVICO_id_servico
    ? servicoNome(fidelidade.SERVICO_id_servico, servicos)
    : produtoNome(fidelidade.PRODUTO_id_produto, produtos);
}
