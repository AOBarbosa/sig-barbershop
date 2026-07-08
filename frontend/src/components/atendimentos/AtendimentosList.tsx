"use client";

import { CalendarClock, Plus, Wallet } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import {
  barbeiroNome,
  clienteNome,
  formatCurrency,
  formatDateTime
} from "@/components/atendimentos/atendimentoFormatters";
import { StatusBadge } from "@/components/atendimentos/StatusBadge";
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
import {
  useAtendimentoLookups,
  useAtendimentos
} from "@/hooks/useAtendimentos";
import type { Atendimento } from "@/types/atendimento";

export function AtendimentosList() {
  const atendimentosQuery = useAtendimentos();
  const lookupsQuery = useAtendimentoLookups();
  const searchParams = useSearchParams();
  const saved = searchParams.get("salvo") === "1";
  const atendimentos = atendimentosQuery.data ?? [];
  const total = atendimentos.reduce(
    (sum, atendimento) => sum + Number(atendimento.valor_total),
    0
  );

  return (
    <section className="space-y-5">
      <AtendimentosHeader saved={saved} />
      <div className="grid gap-4 md:grid-cols-3">
        <SummaryCard
          title="Atendimentos"
          value={String(atendimentos.length)}
          description="Registros carregados"
          icon={CalendarClock}
        />
        <SummaryCard
          title="Agendados"
          value={String(
            atendimentos.filter((item) => item.status === "AGENDADO").length
          )}
          description="Ainda não iniciados"
          icon={CalendarClock}
        />
        <SummaryCard
          title="Valor em agenda"
          value={formatCurrency(total)}
          description="Soma enviada pelo backend"
          icon={Wallet}
        />
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Agenda</CardTitle>
        </CardHeader>
        <CardContent>
          {atendimentosQuery.isError || lookupsQuery.isError ? (
            <Alert variant="destructive">
              <AlertTitle>Erro ao carregar atendimentos</AlertTitle>
              <AlertDescription>
                {atendimentosQuery.error?.message ??
                  lookupsQuery.error?.message}
              </AlertDescription>
            </Alert>
          ) : (
            <AtendimentosTable
              isLoading={atendimentosQuery.isLoading || lookupsQuery.isLoading}
              atendimentos={atendimentos}
              lookups={lookupsQuery.data}
            />
          )}
        </CardContent>
      </Card>
    </section>
  );
}

function AtendimentosHeader({ saved }: { saved: boolean }) {
  return (
    <>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Atendimentos
          </h1>
          <p className="text-muted-foreground text-sm">
            Agenda principal da barbearia com cliente, barbeiro e status.
          </p>
        </div>
        <Button asChild>
          <Link href="/atendimentos/novo">
            <Plus className="size-4" />
            Novo atendimento
          </Link>
        </Button>
      </div>
      {saved ? (
        <Alert>
          <AlertTitle>Atendimento salvo com sucesso</AlertTitle>
          <AlertDescription>A agenda foi atualizada.</AlertDescription>
        </Alert>
      ) : null}
    </>
  );
}

function AtendimentosTable({
  isLoading,
  atendimentos,
  lookups
}: {
  isLoading: boolean;
  atendimentos: Atendimento[];
  lookups: ReturnType<typeof useAtendimentoLookups>["data"];
}) {
  if (isLoading) {
    return <Skeleton className="h-56 w-full" />;
  }

  if (atendimentos.length === 0) {
    return (
      <div className="text-muted-foreground flex min-h-40 items-center justify-center rounded-lg border text-sm">
        Nenhum atendimento encontrado
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Cliente</TableHead>
            <TableHead>Barbeiro</TableHead>
            <TableHead>Data</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Valor</TableHead>
            <TableHead className="text-right">Detalhes</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {atendimentos.map((atendimento) => (
            <TableRow key={atendimento.id_atendimento}>
              <TableCell>
                {clienteNome(atendimento.CLIENTE_PESSOA_id_pessoa, lookups)}
              </TableCell>
              <TableCell>
                {barbeiroNome(atendimento.BARBEIRO_PESSOA_id_pessoa, lookups)}
              </TableCell>
              <TableCell>
                {formatDateTime(atendimento.data_hora_inicio)}
              </TableCell>
              <TableCell>
                <StatusBadge status={atendimento.status} />
              </TableCell>
              <TableCell>{formatCurrency(atendimento.valor_total)}</TableCell>
              <TableCell className="text-right">
                <Button asChild variant="outline" size="sm">
                  <Link href={`/atendimentos/${atendimento.id_atendimento}`}>
                    Abrir
                  </Link>
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
