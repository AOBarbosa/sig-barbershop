import api from "@/lib/axios";
import { getPessoa, getPessoas } from "@/services/clienteService";
import type {
  Barbeiro,
  BarbeiroComPessoa,
  BarbeiroDisponibilidadePayload,
  BarbeiroFormPayload,
  BarbeiroPayload,
  DisponibilidadePayload
} from "@/types/barbeiro";
import type { Pessoa } from "@/types/cliente";
import type { Disponibilidade } from "@/types/atendimento";

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
  return hasKeys(data, ["PESSOA_id_pessoa"]);
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
      apelido: payload.apelido,
      comissao_percentual: payload.comissao_percentual
    })
    .then((response) => response.data);

export const updateBarbeiroApi = (id: number, payload: BarbeiroPayload) =>
  api
    .put<Barbeiro>(`/barbeiros/${id}`, payload)
    .then((response) => response.data);

function separarBarbeiroPayload(payload: BarbeiroFormPayload) {
  const { disponibilidades, ...barbeiroPayload } = payload;
  return {
    disponibilidades,
    barbeiroPayload
  };
}

export async function createBarbeiroWithPessoa(payload: BarbeiroFormPayload) {
  const { disponibilidades, barbeiroPayload } = separarBarbeiroPayload(payload);
  const response = await api.post<unknown>(
    "/barbeiros/completo",
    barbeiroPayload
  );

  if (!isBarbeiroCompletoResponse(response.data)) {
    throw new Error("Resposta inválida ao criar barbeiro");
  }

  const barbeiroId = response.data.barbeiro.PESSOA_id_pessoa;

  await Promise.all(
    disponibilidades.map((disponibilidade) =>
      createDisponibilidade({
        BARBEIRO_PESSOA_id_pessoa: barbeiroId,
        ...disponibilidade
      })
    )
  );

  return response.data;
}

export async function updateBarbeiroWithPessoa(
  barbeiroId: number,
  payload: BarbeiroFormPayload
) {
  const { barbeiroPayload } = separarBarbeiroPayload(payload);
  const response = await api.put<unknown>(
    `/barbeiros/${barbeiroId}/completo`,
    barbeiroPayload
  );

  if (!isBarbeiroCompletoResponse(response.data)) {
    throw new Error("Resposta inválida ao atualizar barbeiro");
  }

  return response.data;
}

export const createDisponibilidade = (payload: DisponibilidadePayload) =>
  api
    .post<Disponibilidade>("/disponibilidades", payload)
    .then((response) => response.data);

export const deleteDisponibilidade = (disponibilidadeId: number) =>
  api.delete(`/disponibilidades/${disponibilidadeId}`).then(() => undefined);

export const getDisponibilidadesDoBarbeiro = (barbeiroId: number) =>
  api
    .get<Disponibilidade[]>(`/barbeiros/${barbeiroId}/disponibilidades`)
    .then((response) => response.data);

export async function saveBarbeiroDisponibilidade(
  barbeiroId: number,
  payload: BarbeiroDisponibilidadePayload[]
) {
  const disponibilidades = await getDisponibilidadesDoBarbeiro(barbeiroId);

  await Promise.all(
    disponibilidades.map((disponibilidade) =>
      deleteDisponibilidade(disponibilidade.id_disponibilidade)
    )
  );

  return Promise.all(
    payload.map((disponibilidade) =>
      createDisponibilidade({
        BARBEIRO_PESSOA_id_pessoa: barbeiroId,
        ...disponibilidade
      })
    )
  );
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
