import api from "@/lib/axios";
import { getPessoa, getPessoas } from "@/services/clienteService";
import type {
  Barbeiro,
  BarbeiroComPessoa,
  BarbeiroFormPayload,
  BarbeiroPayload
} from "@/types/barbeiro";
import type { Pessoa } from "@/types/cliente";

function hasKeys(data: unknown, keys: string[]) {
  return (
    typeof data === "object" &&
    data !== null &&
    keys.every((key) => key in data)
  );
}

function isPessoa(data: unknown): data is Pessoa {
  return hasKeys(data, ["id_pessoa", "nome", "cpf"]);
}

function isBarbeiro(data: unknown): data is Barbeiro {
  return hasKeys(data, ["id_barbeiro", "PESSOA_id_pessoa", "ativo"]);
}

function isBarbeiroCompletoResponse(
  data: unknown
): data is { barbeiro: Barbeiro; pessoa: Pessoa } {
  return (
    hasKeys(data, ["barbeiro", "pessoa"]) &&
    isBarbeiro((data as { barbeiro: unknown }).barbeiro) &&
    isPessoa((data as { pessoa: unknown }).pessoa)
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

export const getBarbeiro = (id: number) =>
  api.get<unknown>(`/barbeiros/${id}`).then((response) => {
    if (!isBarbeiro(response.data)) {
      throw new Error("Resposta inválida ao carregar barbeiro");
    }

    return response.data;
  });

export const createBarbeiroApi = (pessoaId: number, payload: BarbeiroPayload) =>
  api
    .post<Barbeiro>("/barbeiros", {
      PESSOA_id_pessoa: pessoaId,
      especialidade: payload.especialidade,
      ativo: payload.ativo
    })
    .then((response) => response.data);

export const updateBarbeiroApi = (id: number, payload: BarbeiroPayload) =>
  api
    .put<Barbeiro>(`/barbeiros/${id}`, payload)
    .then((response) => response.data);

export async function createBarbeiroWithPessoa(payload: BarbeiroFormPayload) {
  const response = await api.post<unknown>("/barbeiros/completo", payload);

  if (!isBarbeiroCompletoResponse(response.data)) {
    throw new Error("Resposta inválida ao criar barbeiro");
  }

  return response.data;
}

export async function updateBarbeiroWithPessoa(
  barbeiroId: number,
  payload: BarbeiroFormPayload
) {
  const response = await api.put<unknown>(
    `/barbeiros/${barbeiroId}/completo`,
    payload
  );

  if (!isBarbeiroCompletoResponse(response.data)) {
    throw new Error("Resposta inválida ao atualizar barbeiro");
  }

  return response.data;
}

export async function getBarbeirosComPessoas(): Promise<BarbeiroComPessoa[]> {
  const [barbeiros, pessoas] = await Promise.all([
    getBarbeiros(),
    getPessoas()
  ]);
  const pessoasById = new Map(
    pessoas.map((pessoa) => [pessoa.id_pessoa, pessoa])
  );

  return barbeiros.flatMap((barbeiro) => {
    const pessoa = pessoasById.get(barbeiro.PESSOA_id_pessoa);

    if (!pessoa) {
      return [];
    }

    return [{ ...barbeiro, pessoa }];
  });
}

export async function getBarbeiroComPessoa(barbeiroId: number) {
  const barbeiro = await getBarbeiro(barbeiroId);
  const pessoa = await getPessoa(barbeiro.PESSOA_id_pessoa);

  return { barbeiro, pessoa };
}
