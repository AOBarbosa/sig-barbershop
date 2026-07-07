import type React from "react";

import { formatCurrency } from "@/components/atendimentos/atendimentoFormatters";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from "@/components/ui/table";

export function DetailInfo({
  icon: Icon,
  label,
  value
}: {
  icon: React.ElementType;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg border p-4">
      <Icon className="mb-3 size-4" />
      <p className="text-muted-foreground text-xs">{label}</p>
      <p className="font-medium">{value}</p>
    </div>
  );
}

export function ServicosVinculadosTable({
  servicos,
  servicosCatalogo
}: {
  servicos: Array<{ SERVICO_id_servico: number; preco_cobrado: string }>;
  servicosCatalogo: Array<{ id_servico: number; nome: string }>;
}) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Serviço</TableHead>
          <TableHead>Preço cobrado</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {servicos.map((item) => (
          <TableRow key={item.SERVICO_id_servico}>
            <TableCell>
              {servicosCatalogo.find(
                (servico) => servico.id_servico === item.SERVICO_id_servico
              )?.nome ?? "Serviço"}
            </TableCell>
            <TableCell>{formatCurrency(item.preco_cobrado)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
