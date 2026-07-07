"use client";

import { CheckCircle2, Plus, Wallet } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import {
  clienteNome,
  formatCurrency,
  formatDateTime
} from "@/components/vendas/vendaFormatters";
import { StatusBadge } from "@/components/vendas/StatusBadge";
import { SummaryCard } from "@/components/servicos/ServicoListParts";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from "@/components/ui/table";
import { useVendaLookups, useVendas } from "@/hooks/useVendas";
import type { Venda } from "@/types/venda";

export function VendasList() {
  const vendasQuery = useVendas();
  const lookupsQuery = useVendaLookups();
  const searchParams = useSearchParams();
  const saved = searchParams.get("salvo") === "1";
  const vendas = vendasQuery.data ?? [];
  const total = vendas.reduce(
    (sum, venda) => sum + Number(venda.valor_total),
    0
  );
  const concluidas = vendas.filter(
    (venda) => venda.status === "concluida"
  ).length;

  return (
    <section className="space-y-5">
      <VendasHeader saved={saved} />
      <div className="grid gap-4 md:grid-cols-3">
        <SummaryCard
          title="Vendas"
          value={String(vendas.length)}
          description="Registros carregados"
          icon={Wallet}
        />
        <SummaryCard
          title="Concluídas"
          value={String(concluidas)}
          description="Vendas finalizadas"
          icon={CheckCircle2}
        />
        <SummaryCard
          title="Faturamento"
          value={formatCurrency(total)}
          description="Soma enviada pelo backend"
          icon={Wallet}
        />
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Histórico</CardTitle>
        </CardHeader>
        <CardContent>
          {vendasQuery.isError || lookupsQuery.isError ? (
            <Alert variant="destructive">
              <AlertTitle>Erro ao carregar vendas</AlertTitle>
              <AlertDescription>
                {vendasQuery.error?.message ?? lookupsQuery.error?.message}
              </AlertDescription>
            </Alert>
          ) : (
            <VendasTable
              isLoading={vendasQuery.isLoading || lookupsQuery.isLoading}
              vendas={vendas}
              lookups={lookupsQuery.data}
            />
          )}
        </CardContent>
      </Card>
    </section>
  );
}

function VendasHeader({ saved }: { saved: boolean }) {
  return (
    <>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Vendas</h1>
          <p className="text-muted-foreground text-sm">
            Histórico de vendas de produtos no balcão.
          </p>
        </div>
        <Button asChild>
          <Link href="/vendas/novo">
            <Plus className="size-4" />
            Nova venda
          </Link>
        </Button>
      </div>
      {saved ? (
        <Alert>
          <AlertTitle>Venda salva com sucesso</AlertTitle>
          <AlertDescription>O histórico foi atualizado.</AlertDescription>
        </Alert>
      ) : null}
    </>
  );
}

function VendasTable({
  isLoading,
  vendas,
  lookups
}: {
  isLoading: boolean;
  vendas: Venda[];
  lookups: ReturnType<typeof useVendaLookups>["data"];
}) {
  if (isLoading) {
    return <Skeleton className="h-56 w-full" />;
  }

  if (vendas.length === 0) {
    return (
      <div className="text-muted-foreground flex min-h-40 items-center justify-center rounded-lg border text-sm">
        Nenhuma venda encontrada
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Cliente</TableHead>
            <TableHead>Data</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Valor</TableHead>
            <TableHead className="text-right">Detalhes</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {vendas.map((venda) => (
            <TableRow key={venda.id_venda}>
              <TableCell>
                {clienteNome(venda.CLIENTE_id_cliente, lookups)}
              </TableCell>
              <TableCell>{formatDateTime(venda.data_venda)}</TableCell>
              <TableCell>
                <StatusBadge status={venda.status} />
              </TableCell>
              <TableCell>{formatCurrency(venda.valor_total)}</TableCell>
              <TableCell className="text-right">
                <Button asChild variant="outline" size="sm">
                  <Link href={`/vendas/${venda.id_venda}`}>Abrir</Link>
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
