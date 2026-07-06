import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { AtendimentoStatus } from "@/types/atendimento";

import { statusLabel } from "./atendimentoFormatters";

const statusClasses: Record<AtendimentoStatus, string> = {
  agendado: "border-blue-200 bg-blue-50 text-blue-700",
  em_andamento: "border-amber-200 bg-amber-50 text-amber-700",
  concluido: "border-emerald-200 bg-emerald-50 text-emerald-700",
  cancelado: "border-red-200 bg-red-50 text-red-700"
};

export function StatusBadge({ status }: { status: AtendimentoStatus }) {
  return (
    <Badge variant="outline" className={cn("w-fit", statusClasses[status])}>
      {statusLabel(status)}
    </Badge>
  );
}
