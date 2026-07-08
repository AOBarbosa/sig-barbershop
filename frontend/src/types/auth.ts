export type AuthRole = "admin" | "funcionario" | "cliente";

export interface UsuarioAtual {
  id_pessoa: number;
  nome: string;
  email: string | null;
  role: AuthRole;
}

export interface LoginPayload {
  email: string;
  senha: string;
}
