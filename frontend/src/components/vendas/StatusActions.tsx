"use client";

import { Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useUpdateVendaStatus } from "@/hooks/useVendas";
import type { VendaStatus } from "@/types/venda";

const nextActions: Record<
  VendaStatus,
  Array<{ label: string; status: VendaStatus }>
> = {
  pendente: [
    { label: "Concluir", status: "concluida" },
    { label: "Cancelar", status: "cancelada" }
  ],
  concluida: [],
  cancelada: []
};

export function StatusActions({
  vendaId,
  status
}: {
  vendaId: number;
  status: VendaStatus;
}) {
  const mutation = useUpdateVendaStatus(vendaId);
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
          variant={action.status === "cancelada" ? "outline" : "default"}
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
