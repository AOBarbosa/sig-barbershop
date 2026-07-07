import type { ClienteComPessoa } from "@/types/cliente";

export function formatCpf(cpf: string) {
  if (cpf.length !== 11) {
    return cpf;
  }

  return `${cpf.slice(0, 3)}.${cpf.slice(3, 6)}.${cpf.slice(6, 9)}-${cpf.slice(9)}`;
}

export function formatDate(iso: string | null | undefined) {
  if (!iso) {
    return "—";
  }

  const [year, month, day] = iso.slice(0, 10).split("-");
  return `${day}/${month}/${year}`;
}

export function getClientesComEmail(clientes: ClienteComPessoa[]) {
  return clientes.filter((cliente) => cliente.pessoa.email).length;
}
