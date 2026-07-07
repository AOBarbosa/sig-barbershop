"use client";

import {
  ArrowLeft,
  CalendarClock,
  CreditCard,
  UserRound,
  Wallet
} from "lucide-react";
import Link from "next/link";

import {
  caixaLabel,
  clienteNome,
  formaPagamentoLabel,
  formatCurrency,
  formatDateTime
} from "@/components/vendas/vendaFormatters";
import {
  DetailInfo,
  ProdutosVinculadosTable
} from "@/components/vendas/VendaDetailParts";
import { StatusActions } from "@/components/vendas/StatusActions";
import { StatusBadge } from "@/components/vendas/StatusBadge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useVenda, useVendaLookups, useVendaProdutos } from "@/hooks/useVendas";

export function VendaDetail({ vendaId }: { vendaId: number }) {
  const vendaQuery = useVenda(vendaId);
  const produtosQuery = useVendaProdutos(vendaId);
  const lookupsQuery = useVendaLookups();

  if (vendaQuery.isLoading || lookupsQuery.isLoading) {
    return <Skeleton className="h-96 w-full" />;
  }

  if (vendaQuery.isError || lookupsQuery.isError) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Venda não carregada</AlertTitle>
        <AlertDescription>
          {vendaQuery.error?.message ?? lookupsQuery.error?.message}
        </AlertDescription>
      </Alert>
    );
  }

  const venda = vendaQuery.data;
  const lookups = lookupsQuery.data;

  if (!venda || !lookups) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Dados não encontrados</AlertTitle>
        <AlertDescription>
          Não foi possível montar os detalhes da venda.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <section className="space-y-5">
      <Button asChild variant="ghost" className="px-0">
        <Link href="/vendas">
          <ArrowLeft className="size-4" />
          Voltar para vendas
        </Link>
      </Button>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Venda #{venda.id_venda}
          </h1>
          <p className="text-muted-foreground text-sm">
            Total, produtos e transições de status da venda.
          </p>
        </div>
        <StatusBadge status={venda.status} />
      </div>
      <div className="grid gap-4 lg:grid-cols-[1fr_20rem]">
        <Card>
          <CardHeader>
            <CardTitle>Dados da venda</CardTitle>
            <CardDescription>
              Total calculado pelo backend e retornado pela API.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4 sm:grid-cols-3">
            <DetailInfo
              icon={UserRound}
              label="Cliente"
              value={clienteNome(venda.CLIENTE_id_cliente, lookups)}
            />
            <DetailInfo
              icon={CalendarClock}
              label="Data"
              value={formatDateTime(venda.data_venda)}
            />
            <DetailInfo
              icon={CreditCard}
              label="Forma de pagamento"
              value={formaPagamentoLabel(venda.forma_pagamento)}
            />
            <DetailInfo
              icon={UserRound}
              label="Caixa"
              value={caixaLabel(venda.CAIXA_id_caixa, lookups)}
            />
            <div className="rounded-lg border p-4 sm:col-span-2">
              <div className="mb-2 flex items-center gap-2">
                <Wallet className="size-4" />
                <p className="text-sm font-medium">
                  Total calculado pelo backend
                </p>
              </div>
              <p className="text-3xl font-semibold">
                {formatCurrency(venda.valor_total)}
              </p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Status</CardTitle>
            <CardDescription>Conclua ou cancele a venda.</CardDescription>
          </CardHeader>
          <CardContent>
            <StatusActions vendaId={venda.id_venda} status={venda.status} />
          </CardContent>
        </Card>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Produtos vinculados</CardTitle>
        </CardHeader>
        <CardContent>
          {produtosQuery.isLoading ? (
            <Skeleton className="h-32 w-full" />
          ) : (
            <ProdutosVinculadosTable
              itens={produtosQuery.data ?? []}
              produtosCatalogo={lookups.produtos}
            />
          )}
        </CardContent>
      </Card>
    </section>
  );
}
