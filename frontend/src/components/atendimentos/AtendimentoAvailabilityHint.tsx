import type { Disponibilidade } from "@/types/atendimento";

export function AtendimentoAvailabilityHint({
  disponibilidades
}: {
  disponibilidades?: Disponibilidade[];
}) {
  if (!disponibilidades?.length) {
    return (
      <div className="text-muted-foreground rounded-lg border p-3 text-sm">
        Selecione um barbeiro para ver a disponibilidade.
      </div>
    );
  }

  const [disponibilidade] = disponibilidades;

  return (
    <div className="text-muted-foreground rounded-lg border p-3 text-sm">
      Disponível em {disponibilidade.dia_semana}, das{" "}
      {disponibilidade.hora_inicio.slice(0, 5)} às{" "}
      {disponibilidade.hora_fim.slice(0, 5)}
    </div>
  );
}
