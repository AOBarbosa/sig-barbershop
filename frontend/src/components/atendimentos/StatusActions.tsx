"use client";

import { Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useUpdateAtendimentoStatus } from "@/hooks/useAtendimentos";
import type { AtendimentoStatus } from "@/types/atendimento";

const nextActions: Record<
  AtendimentoStatus,
  Array<{ label: string; status: AtendimentoStatus }>
> = {
  AGENDADO: [
    { label: "Iniciar", status: "EM_EXECUCAO" },
    { label: "Cancelar", status: "CANCELADO" }
  ],
  EM_EXECUCAO: [
    { label: "Concluir", status: "CONCLUIDO" },
    { label: "Cancelar", status: "CANCELADO" }
  ],
  CONCLUIDO: [],
  CANCELADO: []
};

export function StatusActions({
  atendimentoId,
  status
}: {
  atendimentoId: number;
  status: AtendimentoStatus;
}) {
  const mutation = useUpdateAtendimentoStatus(atendimentoId);
  const actions = nextActions[status];

  if (actions.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-wrap gap-2">
      {actions.map((action) => (
        <Button
          key={action.status}
          type="button"
          variant={action.status === "CANCELADO" ? "outline" : "default"}
          disabled={mutation.isPending}
          onClick={() => mutation.mutate(action.status)}>
          {mutation.isPending ? (
            <Loader2 className="size-4 animate-spin" />
          ) : null}
          {action.label}
        </Button>
      ))}
    </div>
  );
}
