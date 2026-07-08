export interface Produto {
  id_produto: number;
  nome: string;
  categoria: string | null;
  ativo: boolean;
  preco_venda: string | number;
  preco_custo: string | number;
  pontos_gerados: number;
}

export interface ProdutoPayload {
  nome: string;
  categoria: string | null;
  ativo: boolean;
  preco_venda: number;
  preco_custo: number;
  pontos_gerados: number;
}
