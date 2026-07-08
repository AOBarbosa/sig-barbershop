import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { VendaStatus } from "@/types/venda";

import { statusLabel } from "./vendaFormatters";

const statusClasses: Record<VendaStatus, string> = {
  ABERTA: "border-amber-200 bg-amber-50 text-amber-700",
  PAGA: "border-emerald-200 bg-emerald-50 text-emerald-700",
  CANCELADA: "border-red-200 bg-red-50 text-red-700",
  ESTORNADA: "border-slate-200 bg-slate-50 text-slate-700"
};

export function StatusBadge({ status }: { status: VendaStatus }) {
  return (
    <Badge variant="outline" className={cn("w-fit", statusClasses[status])}>
      {statusLabel(status)}
    </Badge>
  );
}
