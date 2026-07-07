import api from "@/lib/axios";
import type {
  Cliente,
  ClienteComPessoa,
  ClienteFormPayload,
  Pessoa,
  PessoaPayload
} from "@/types/cliente";

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

function isCliente(data: unknown): data is Cliente {
  return hasKeys(data, ["id_cliente", "PESSOA_id_pessoa"]);
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

export const getPessoas = () =>
  api
    .get<unknown>("/pessoas")
    .then((response) =>
      parseList(response.data, isPessoa, "Resposta inválida ao listar pessoas")
    );

export const getPessoa = (id: number) =>
  api.get<unknown>(`/pessoas/${id}`).then((response) => {
    if (!isPessoa(response.data)) {
      throw new Error("Resposta inválida ao carregar pessoa");
    }

    return response.data;
  });

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

export const getCliente = (id: number) =>
  api.get<unknown>(`/clientes/${id}`).then((response) => {
    if (!isCliente(response.data)) {
      throw new Error("Resposta inválida ao carregar cliente");
    }

    return response.data;
  });

export const createPessoa = (payload: PessoaPayload) =>
  api.post<Pessoa>("/pessoas", payload).then((response) => response.data);

export const updatePessoa = (id: number, payload: PessoaPayload) =>
  api.put<Pessoa>(`/pessoas/${id}`, payload).then((response) => response.data);

export const createClienteApi = (pessoaId: number) =>
  api
    .post<Cliente>("/clientes", { PESSOA_id_pessoa: pessoaId })
    .then((response) => response.data);

function isClienteCompletoResponse(
  data: unknown
): data is { cliente: Cliente; pessoa: Pessoa } {
  return (
    hasKeys(data, ["cliente", "pessoa"]) &&
    isCliente((data as { cliente: unknown }).cliente) &&
    isPessoa((data as { pessoa: unknown }).pessoa)
  );
}

export async function createClienteWithPessoa(payload: ClienteFormPayload) {
  const response = await api.post<unknown>("/clientes/completo", payload);

  if (!isClienteCompletoResponse(response.data)) {
    throw new Error("Resposta inválida ao criar cliente");
  }

  return response.data;
}

export async function getClientesComPessoas(): Promise<ClienteComPessoa[]> {
  const [clientes, pessoas] = await Promise.all([getClientes(), getPessoas()]);
  const pessoasById = new Map(
    pessoas.map((pessoa) => [pessoa.id_pessoa, pessoa])
  );

  return clientes.flatMap((cliente) => {
    const pessoa = pessoasById.get(cliente.PESSOA_id_pessoa);

    if (!pessoa) {
      return [];
    }

    return [{ ...cliente, pessoa }];
  });
}
