import api from "@/lib/axios";
import type {
  Atendimento,
  AtendimentoFormPayload,
  AtendimentoPayload,
  AtendimentoServico,
  AtendimentoStatus,
  Barbeiro,
  Cliente,
  Disponibilidade,
  Pessoa
} from "@/types/atendimento";

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

function isAtendimento(data: unknown): data is Atendimento {
  return hasKeys(data, [
    "id_atendimento",
    "CLIENTE_PESSOA_id_pessoa",
    "BARBEIRO_PESSOA_id_pessoa",
    "data_hora_inicio",
    "status",
    "valor_total"
  ]);
}

function isPessoa(data: unknown): data is Pessoa {
  return hasKeys(data, ["id_pessoa", "nome", "cpf"]);
}

function isCliente(data: unknown): data is Cliente {
  return hasKeys(data, ["PESSOA_id_pessoa"]);
}

function isBarbeiro(data: unknown): data is Barbeiro {
  return hasKeys(data, ["PESSOA_id_pessoa"]);
}

function isDisponibilidade(data: unknown): data is Disponibilidade {
  return hasKeys(data, [
    "id_disponibilidade",
    "BARBEIRO_PESSOA_id_pessoa",
    "dia_semana"
  ]);
}

function isAtendimentoServico(data: unknown): data is AtendimentoServico {
  return hasKeys(data, [
    "ATENDIMENTO_id_atendimento",
    "SERVICO_id_servico",
    "preco_cobrado"
  ]);
}

export const getAtendimentos = () =>
  api
    .get<unknown>("/atendimentos")
    .then((response) =>
      parseList(
        response.data,
        isAtendimento,
        "Resposta inválida ao listar atendimentos"
      )
    );

export const getAtendimento = (id: number) =>
  api.get<unknown>(`/atendimentos/${id}`).then((response) => {
    if (!isAtendimento(response.data)) {
      throw new Error("Resposta inválida ao carregar atendimento");
    }

    return response.data;
  });

export const getAtendimentoServicos = (id: number) =>
  api
    .get<unknown>(`/atendimentos/${id}/servicos`)
    .then((response) =>
      parseList(
        response.data,
        isAtendimentoServico,
        "Resposta inválida ao listar serviços do atendimento"
      )
    );

export const getPessoas = () =>
  api
    .get<unknown>("/pessoas")
    .then((response) =>
      parseList(response.data, isPessoa, "Resposta inválida ao listar pessoas")
    );

export const getClientes = () =>
  api
    .get<unknown>("/clientes")
    .then((response) =>
      parseList(
        response.data,
        isCliente,
        "Resposta inválida ao listar clientes"
      )
    );

export const getBarbeiros = () =>
  api
    .get<unknown>("/barbeiros")
    .then((response) =>
      parseList(
        response.data,
        isBarbeiro,
        "Resposta inválida ao listar barbeiros"
      )
    );

export const getDisponibilidadesDoBarbeiro = (barbeiroId: number) =>
  api
    .get<unknown>(`/barbeiros/${barbeiroId}/disponibilidades`)
    .then((response) =>
      parseList(
        response.data,
        isDisponibilidade,
        "Resposta inválida ao listar disponibilidades"
      )
    );

export const createAtendimento = (payload: AtendimentoPayload) =>
  api
    .post<Atendimento>("/atendimentos", payload)
    .then((response) => response.data);

export const addAtendimentoServico = (
  atendimentoId: number,
  servicoId: number
) =>
  api
    .post<AtendimentoServico>(`/atendimentos/${atendimentoId}/servicos`, {
      SERVICO_id_servico: servicoId
    })
    .then((response) => response.data);

export async function createAtendimentoWithServicos(
  payload: AtendimentoFormPayload
) {
  const { servicoIds, ...atendimentoPayload } = payload;
  const atendimento = await createAtendimento(atendimentoPayload);

  await Promise.all(
    servicoIds.map((servicoId) =>
      addAtendimentoServico(atendimento.id_atendimento, servicoId)
    )
  );

  return atendimento;
}

export const updateAtendimentoStatus = (
  atendimentoId: number,
  status: AtendimentoStatus
) =>
  api
    .patch<Atendimento>(`/atendimentos/${atendimentoId}/status`, { status })
    .then((response) => response.data);
