import type { BarbeiroComPessoa } from "@/types/barbeiro";

export { formatCpf, formatDate } from "@/components/clientes/clienteFormatters";

export function getBarbeirosAtivos(barbeiros: BarbeiroComPessoa[]) {
  return barbeiros.length;
}

export function getEspecialidadesUnicas(barbeiros: BarbeiroComPessoa[]) {
  const apelidos = barbeiros
    .map((barbeiro) => barbeiro.apelido)
    .filter((value): value is string => Boolean(value));

  return new Set(apelidos).size;
}
