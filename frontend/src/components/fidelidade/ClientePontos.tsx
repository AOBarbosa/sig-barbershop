"use client";

import { ArrowLeft, History, Star } from "lucide-react";
import Link from "next/link";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from "@/components/ui/table";
import { useCliente, usePessoaDoCliente } from "@/hooks/useClientes";
import { useHistoricoPontos, useSaldoPontos } from "@/hooks/useHistoricoPontos";

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short"
  }).format(new Date(value));
}

function tipoLabel(tipo: "acumulo" | "resgate") {
  return tipo === "acumulo" ? "Acúmulo" : "Resgate";
}

export function ClientePontos({ clienteId }: { clienteId: number }) {
  const clienteQuery = useCliente(clienteId);
  const pessoaQuery = usePessoaDoCliente(clienteQuery.data?.PESSOA_id_pessoa);
  const saldoQuery = useSaldoPontos(clienteId);
  const historicoQuery = useHistoricoPontos(clienteId);

  if (clienteQuery.isLoading || pessoaQuery.isLoading) {
    return <Skeleton className="h-96 w-full" />;
  }

  if (clienteQuery.isError || pessoaQuery.isError) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Cliente não carregado</AlertTitle>
        <AlertDescription>
          {clienteQuery.error?.message ?? pessoaQuery.error?.message}
        </AlertDescription>
      </Alert>
    );
  }

  const pessoa = pessoaQuery.data;

  return (
    <section className="space-y-5">
      <Button asChild variant="ghost" className="px-0">
        <Link href="/clientes">
          <ArrowLeft className="size-4" />
          Voltar para clientes
        </Link>
      </Button>
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">
          Pontos de {pessoa?.nome ?? "cliente"}
        </h1>
        <p className="text-muted-foreground text-sm">
          Saldo atual e extrato de movimentações de fidelidade.
        </p>
      </div>
      <Card>
        <CardHeader className="flex flex-row items-center gap-3 space-y-0">
          <div className="bg-muted flex size-9 items-center justify-center rounded-lg">
            <Star className="size-4" />
          </div>
          <div>
            <CardDescription>Saldo atual</CardDescription>
            <CardTitle className="text-2xl">
              {saldoQuery.isLoading
                ? "…"
                : `${saldoQuery.data?.saldo ?? 0} pts`}
            </CardTitle>
          </div>
        </CardHeader>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="size-4" />
            Extrato
          </CardTitle>
        </CardHeader>
        <CardContent>
          {historicoQuery.isLoading ? (
            <Skeleton className="h-40 w-full" />
          ) : (
            <ExtratoTable itens={historicoQuery.data ?? []} />
          )}
        </CardContent>
      </Card>
    </section>
  );
}

function ExtratoTable({
  itens
}: {
  itens: ReturnType<typeof useHistoricoPontos>["data"];
}) {
  const historico = itens ?? [];

  if (historico.length === 0) {
    return (
      <div className="text-muted-foreground flex min-h-24 items-center justify-center rounded-lg border text-sm">
        Nenhuma movimentação encontrada
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Data</TableHead>
          <TableHead>Tipo</TableHead>
          <TableHead>Pontos</TableHead>
          <TableHead>Descrição</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {historico.map((item) => (
          <TableRow key={item.id_historico}>
            <TableCell>{formatDateTime(item.data_movimentacao)}</TableCell>
            <TableCell>
              <Badge
                variant={
                  item.tipo_movimentacao === "acumulo" ? "secondary" : "outline"
                }>
                {tipoLabel(item.tipo_movimentacao)}
              </Badge>
            </TableCell>
            <TableCell>{item.pontos} pts</TableCell>
            <TableCell className="text-muted-foreground">
              {item.descricao || "—"}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
