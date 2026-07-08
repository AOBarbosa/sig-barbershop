import api from "@/lib/axios";
import type { Servico, ServicoPayload } from "@/types/servico";

function isServico(data: unknown): data is Servico {
  return (
    typeof data === "object" &&
    data !== null &&
    "id_servico" in data &&
    "nome" in data &&
    "ativo" in data
  );
}

function parseServico(data: unknown) {
  if (!isServico(data)) {
    throw new Error("Resposta inválida ao carregar serviço");
  }

  return data;
}

function parseServicos(data: unknown) {
  if (!Array.isArray(data) || !data.every(isServico)) {
    throw new Error("Resposta inválida ao listar serviços");
  }

  return data;
}

export const getServicos = () =>
  api
    .get<unknown>("/servicos")
    .then((response) => parseServicos(response.data));

export const getServico = (id: number) =>
  api
    .get<unknown>(`/servicos/${id}`)
    .then((response) => parseServico(response.data));

export const createServico = (payload: ServicoPayload) =>
  api.post<Servico>("/servicos", payload).then((response) => response.data);

export const updateServico = (id: number, payload: ServicoPayload) =>
  api
    .put<Servico>(`/servicos/${id}`, payload)
    .then((response) => response.data);
