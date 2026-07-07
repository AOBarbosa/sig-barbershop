import type { BarbeiroComPessoa } from "@/types/barbeiro";

export {
  formatCpf,
  formatDate
} from "@/components/clientes/clienteFormatters";

export function getBarbeirosAtivos(barbeiros: BarbeiroComPessoa[]) {
  return barbeiros.filter((barbeiro) => barbeiro.ativo).length;
}

export function getEspecialidadesUnicas(barbeiros: BarbeiroComPessoa[]) {
  const especialidades = barbeiros
    .map((barbeiro) => barbeiro.especialidade)
    .filter((value): value is string => Boolean(value));

  return new Set(especialidades).size;
}
