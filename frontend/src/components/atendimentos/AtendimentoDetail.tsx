"use client";

import { ArrowLeft, CalendarClock, UserRound, Wallet } from "lucide-react";
import Link from "next/link";

import {
  barbeiroNome,
  clienteNome,
  formatCurrency,
  formatDateTime
} from "@/components/atendimentos/atendimentoFormatters";
import {
  DetailInfo,
  ServicosVinculadosTable
} from "@/components/atendimentos/AtendimentoDetailParts";
import { AtendimentoMissingDataAlert } from "@/components/atendimentos/AtendimentoMissingDataAlert";
import { StatusActions } from "@/components/atendimentos/StatusActions";
import { StatusBadge } from "@/components/atendimentos/StatusBadge";
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
import {
  useAtendimento,
  useAtendimentoLookups,
  useAtendimentoServicos
} from "@/hooks/useAtendimentos";

export function AtendimentoDetail({
  atendimentoId
}: {
  atendimentoId: number;
}) {
  const atendimentoQuery = useAtendimento(atendimentoId);
  const servicosQuery = useAtendimentoServicos(atendimentoId);
  const lookupsQuery = useAtendimentoLookups();

  if (atendimentoQuery.isLoading || lookupsQuery.isLoading) {
    return <Skeleton className="h-96 w-full" />;
  }

  if (atendimentoQuery.isError || lookupsQuery.isError) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Atendimento não carregado</AlertTitle>
        <AlertDescription>
          {atendimentoQuery.error?.message ?? lookupsQuery.error?.message}
        </AlertDescription>
      </Alert>
    );
  }

  const atendimento = atendimentoQuery.data;
  const lookups = lookupsQuery.data;

  if (!atendimento || !lookups) {
    return (
      <AtendimentoMissingDataAlert message="Não foi possível montar os detalhes do atendimento." />
    );
  }

  return (
    <section className="space-y-5">
      <Button asChild variant="ghost" className="px-0">
        <Link href="/atendimentos">
          <ArrowLeft className="size-4" />
          Voltar para atendimentos
        </Link>
      </Button>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Atendimento #{atendimento.id_atendimento}
          </h1>
          <p className="text-muted-foreground text-sm">
            Valor, serviços e transições de status do atendimento.
          </p>
        </div>
        <StatusBadge status={atendimento.status} />
      </div>
      <div className="grid gap-4 lg:grid-cols-[1fr_20rem]">
        <Card>
          <CardHeader>
            <CardTitle>Dados do atendimento</CardTitle>
            <CardDescription>
              Total calculado pelo backend e retornado pela API.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4 sm:grid-cols-3">
            <DetailInfo
              icon={UserRound}
              label="Cliente"
              value={clienteNome(atendimento.CLIENTE_id_cliente, lookups)}
            />
            <DetailInfo
              icon={UserRound}
              label="Barbeiro"
              value={barbeiroNome(atendimento.BARBEIRO_id_barbeiro, lookups)}
            />
            <DetailInfo
              icon={CalendarClock}
              label="Data"
              value={formatDateTime(atendimento.data_hora)}
            />
            <div className="rounded-lg border p-4 sm:col-span-3">
              <div className="mb-2 flex items-center gap-2">
                <Wallet className="size-4" />
                <p className="text-sm font-medium">
                  Total calculado pelo backend
                </p>
              </div>
              <p className="text-3xl font-semibold">
                {formatCurrency(atendimento.valor_total)}
              </p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Status</CardTitle>
            <CardDescription>Avance ou cancele o atendimento.</CardDescription>
          </CardHeader>
          <CardContent>
            <StatusActions
              atendimentoId={atendimento.id_atendimento}
              status={atendimento.status}
            />
          </CardContent>
        </Card>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Serviços vinculados</CardTitle>
        </CardHeader>
        <CardContent>
          {servicosQuery.isLoading ? (
            <Skeleton className="h-32 w-full" />
          ) : (
            <ServicosVinculadosTable
              servicos={servicosQuery.data ?? []}
              servicosCatalogo={lookups.servicos}
            />
          )}
        </CardContent>
      </Card>
    </section>
  );
}
