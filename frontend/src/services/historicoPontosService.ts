import api from "@/lib/axios";
import type { HistoricoPontos, SaldoPontos } from "@/types/historicoPontos";

function hasKeys(data: unknown, keys: string[]) {
  return (
    typeof data === "object" &&
    data !== null &&
    keys.every((key) => key in data)
  );
}

function isSaldoPontos(data: unknown): data is SaldoPontos {
  return hasKeys(data, ["CLIENTE_id_cliente", "saldo"]);
}

function isHistoricoPontos(data: unknown): data is HistoricoPontos {
  return hasKeys(data, [
    "id_historico",
    "CLIENTE_id_cliente",
    "pontos",
    "tipo_movimentacao",
    "data_movimentacao"
  ]);
}

export const getSaldoPontos = (clienteId: number) =>
  api.get<unknown>(`/clientes/${clienteId}/pontos`).then((response) => {
    if (!isSaldoPontos(response.data)) {
      throw new Error("Resposta inválida ao carregar saldo de pontos");
    }

    return response.data;
  });

export const getHistoricoPontos = (clienteId: number) =>
  api
    .get<unknown>(`/clientes/${clienteId}/pontos/historico`)
    .then((response) => {
      if (
        !Array.isArray(response.data) ||
        !response.data.every(isHistoricoPontos)
      ) {
        throw new Error("Resposta inválida ao listar histórico de pontos");
      }

      return response.data;
    });
