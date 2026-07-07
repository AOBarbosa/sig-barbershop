export interface Produto {
  id_produto: number;
  nome: string;
  descricao: string | null;
  preco: string;
  estoque: number;
  ativo: boolean;
}

export interface ProdutoPayload {
  nome: string;
  descricao: string;
  preco: number;
  estoque: number;
  ativo: boolean;
}
