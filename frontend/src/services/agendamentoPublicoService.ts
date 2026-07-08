import { gerarHorariosPublicos } from "@/components/atendimentos/atendimentoSlots";
import api from "@/lib/axios";
import { getDisponibilidadesDoBarbeiro } from "@/services/barbeiroService";
import { getPessoas } from "@/services/clienteService";
import { getBarbeiros } from "@/services/barbeiroService";
import type {
  AgendamentoCatalogo,
  AgendamentoHorarios,
  HorarioOcupado
} from "@/types/agendamentoPublico";

function rangePublico() {
  const inicio = new Date();
  inicio.setHours(0, 0, 0, 0);
  const fim = new Date(inicio);
  fim.setDate(inicio.getDate() + 14);
  fim.setHours(23, 59, 59, 0);

  return {
    fim: fim.toISOString().slice(0, 19),
    inicio: inicio.toISOString().slice(0, 19)
  };
}

export async function getCatalogoAgendamento(): Promise<AgendamentoCatalogo> {
  const [barbeiros, pessoas] = await Promise.all([
    getBarbeiros(),
    getPessoas()
  ]);
  const pessoasById = new Map(
    pessoas.map((pessoa) => [pessoa.id_pessoa, pessoa])
  );

  return {
    barbeiros: barbeiros.flatMap((barbeiro) => {
      const pessoa = pessoasById.get(barbeiro.PESSOA_id_pessoa);
      return pessoa ? [{ ...barbeiro, pessoa }] : [];
    })
  };
}

export async function getHorariosAgendamento(
  barbeiroId: number
): Promise<AgendamentoHorarios> {
  const range = rangePublico();
  const [disponibilidades, ocupados] = await Promise.all([
    getDisponibilidadesDoBarbeiro(barbeiroId),
    api
      .get<HorarioOcupado[]>(`/barbeiros/${barbeiroId}/horarios-ocupados`, {
        params: range
      })
      .then((response) => response.data)
  ]);

  return {
    disponibilidades,
    horarios: gerarHorariosPublicos({
      disponibilidades,
      horariosOcupados: ocupados.map((item) => item.data_hora_inicio)
    })
  };
}
