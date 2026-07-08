import api from "@/lib/axios";
import type { LoginPayload, UsuarioAtual } from "@/types/auth";

function hasKeys(data: unknown, keys: string[]) {
  return (
    typeof data === "object" &&
    data !== null &&
    keys.every((key) => key in data)
  );
}

function isUsuarioAtual(data: unknown): data is UsuarioAtual {
  return hasKeys(data, ["id_pessoa", "nome", "role"]);
}

function parseUsuarioAtual(data: unknown) {
  if (!isUsuarioAtual(data)) {
    throw new Error("Resposta inválida de autenticação");
  }

  return data;
}

export const login = (payload: LoginPayload) =>
  api
    .post<unknown>("/auth/login", payload)
    .then((response) => parseUsuarioAtual(response.data));

export const getCurrentUser = () =>
  api
    .get<unknown>("/auth/me")
    .then((response) => parseUsuarioAtual(response.data));

export const logout = () => api.post("/auth/logout").then(() => undefined);
