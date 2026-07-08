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

export interface RegistroClientePayload extends LoginPayload {
  nome: string;
  cpf: string | null;
  data_nascimento?: string | null;
  preferencias?: string | null;
  observacoes?: string | null;
}
