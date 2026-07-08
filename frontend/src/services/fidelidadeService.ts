import api from "@/lib/axios";
import type { Fidelidade, FidelidadePayload } from "@/types/fidelidade";

function hasKeys(data: unknown, keys: string[]) {
  return (
    typeof data === "object" &&
    data !== null &&
    keys.every((key) => key in data)
  );
}

function isFidelidade(data: unknown): data is Fidelidade {
  return hasKeys(data, [
    "id_fidelidade",
    "pontos_acumulados",
    "pontos_uso",
    "ativo"
  ]);
}

function parseList(data: unknown) {
  if (!Array.isArray(data) || !data.every(isFidelidade)) {
    throw new Error("Resposta inválida ao listar regras de fidelidade");
  }

  return data;
}

export const getFidelidades = () =>
  api.get<unknown>("/fidelidades").then((response) => parseList(response.data));

export const getFidelidade = (id: number) =>
  api.get<unknown>(`/fidelidades/${id}`).then((response) => {
    if (!isFidelidade(response.data)) {
      throw new Error("Resposta inválida ao carregar regra de fidelidade");
    }

    return response.data;
  });

export const createFidelidade = (payload: FidelidadePayload) =>
  api
    .post<Fidelidade>("/fidelidades", payload)
    .then((response) => response.data);

export const updateFidelidade = (id: number, payload: FidelidadePayload) =>
  api
    .put<Fidelidade>(`/fidelidades/${id}`, payload)
    .then((response) => response.data);
