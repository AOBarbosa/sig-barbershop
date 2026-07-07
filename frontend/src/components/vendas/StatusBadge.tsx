import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { VendaStatus } from "@/types/venda";

import { statusLabel } from "./vendaFormatters";

const statusClasses: Record<VendaStatus, string> = {
  pendente: "border-amber-200 bg-amber-50 text-amber-700",
  concluida: "border-emerald-200 bg-emerald-50 text-emerald-700",
  cancelada: "border-red-200 bg-red-50 text-red-700"
};

export function StatusBadge({ status }: { status: VendaStatus }) {
  return (
    <Badge variant="outline" className={cn("w-fit", statusClasses[status])}>
      {statusLabel(status)}
    </Badge>
  );
}
