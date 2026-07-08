import api from "@/lib/axios";
import type { Produto, ProdutoPayload } from "@/types/produto";

function isProduto(data: unknown): data is Produto {
  return (
    typeof data === "object" &&
    data !== null &&
    "id_produto" in data &&
    "nome" in data &&
    "ativo" in data
  );
}

function parseProduto(data: unknown) {
  if (!isProduto(data)) {
    throw new Error("Resposta inválida ao carregar produto");
  }

  return data;
}

function parseProdutos(data: unknown) {
  if (!Array.isArray(data) || !data.every(isProduto)) {
    throw new Error("Resposta inválida ao listar produtos");
  }

  return data;
}

export const getProdutos = () =>
  api
    .get<unknown>("/produtos")
    .then((response) => parseProdutos(response.data));

export const getProduto = (id: number) =>
  api
    .get<unknown>(`/produtos/${id}`)
    .then((response) => parseProduto(response.data));

export const createProduto = (payload: ProdutoPayload) =>
  api.post<Produto>("/produtos", payload).then((response) => response.data);

export const updateProduto = (id: number, payload: ProdutoPayload) =>
  api
    .put<Produto>(`/produtos/${id}`, payload)
    .then((response) => response.data);
