import api from "@/lib/axios";
import type {
  Caixa,
  Venda,
  VendaItemPayload,
  VendaFormPayload,
  VendaPayload,
  VendaProduto,
  VendaStatus
} from "@/types/venda";

function hasKeys(data: unknown, keys: string[]) {
  return (
    typeof data === "object" &&
    data !== null &&
    keys.every((key) => key in data)
  );
}

function parseList<T>(
  data: unknown,
  isItem: (item: unknown) => item is T,
  message: string
) {
  if (!Array.isArray(data) || !data.every(isItem)) {
    throw new Error(message);
  }

  return data;
}

function isVenda(data: unknown): data is Venda {
  return hasKeys(data, [
    "id_venda",
    "CLIENTE_id_cliente",
    "CAIXA_id_caixa",
    "data_venda",
    "status",
    "valor_total"
  ]);
}

function isVendaProduto(data: unknown): data is VendaProduto {
  return hasKeys(data, [
    "id_venda_produto",
    "VENDA_id_venda",
    "PRODUTO_id_produto",
    "quantidade",
    "preco_unitario"
  ]);
}

function isCaixa(data: unknown): data is Caixa {
  return hasKeys(data, ["id_caixa", "PESSOA_id_pessoa"]);
}

export const getVendas = () =>
  api
    .get<unknown>("/vendas")
    .then((response) =>
      parseList(response.data, isVenda, "Resposta inválida ao listar vendas")
    );

export const getVenda = (id: number) =>
  api.get<unknown>(`/vendas/${id}`).then((response) => {
    if (!isVenda(response.data)) {
      throw new Error("Resposta inválida ao carregar venda");
    }

    return response.data;
  });

export const getVendaProdutos = (id: number) =>
  api
    .get<unknown>(`/vendas/${id}/produtos`)
    .then((response) =>
      parseList(
        response.data,
        isVendaProduto,
        "Resposta inválida ao listar produtos da venda"
      )
    );

export const getCaixas = () =>
  api
    .get<unknown>("/caixas")
    .then((response) =>
      parseList(response.data, isCaixa, "Resposta inválida ao listar caixas")
    );

export const createVenda = (payload: VendaPayload) =>
  api.post<Venda>("/vendas", payload).then((response) => response.data);

export const addVendaProduto = (vendaId: number, item: VendaItemPayload) =>
  api
    .post<VendaProduto>(`/vendas/${vendaId}/produtos`, item)
    .then((response) => response.data);

export async function createVendaWithProdutos(payload: VendaFormPayload) {
  const { itens, ...vendaPayload } = payload;
  const venda = await createVenda(vendaPayload);

  await Promise.all(itens.map((item) => addVendaProduto(venda.id_venda, item)));

  return venda;
}

export const updateVendaStatus = (vendaId: number, status: VendaStatus) =>
  api
    .patch<Venda>(`/vendas/${vendaId}/status`, { status })
    .then((response) => response.data);
