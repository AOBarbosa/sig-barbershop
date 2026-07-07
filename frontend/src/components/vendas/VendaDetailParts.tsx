import type React from "react";

import { formatCurrency } from "@/components/vendas/vendaFormatters";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from "@/components/ui/table";
import type { Produto } from "@/types/produto";
import type { VendaProduto } from "@/types/venda";

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

export function ProdutosVinculadosTable({
  itens,
  produtosCatalogo
}: {
  itens: VendaProduto[];
  produtosCatalogo: Produto[];
}) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Produto</TableHead>
          <TableHead>Quantidade</TableHead>
          <TableHead>Preço unitário</TableHead>
          <TableHead>Subtotal</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {itens.map((item) => (
          <TableRow key={item.id_venda_produto}>
            <TableCell>
              {produtosCatalogo.find(
                (produto) => produto.id_produto === item.PRODUTO_id_produto
              )?.nome ?? "Produto"}
            </TableCell>
            <TableCell>{item.quantidade}</TableCell>
            <TableCell>{formatCurrency(item.preco_unitario)}</TableCell>
            <TableCell>
              {formatCurrency(Number(item.preco_unitario) * item.quantidade)}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
