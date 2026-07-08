"use client";

import { Plus, Star } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import {
  origemLabel,
  origemNome
} from "@/components/fidelidade/fidelidadeFormatters";
import { SummaryCard } from "@/components/servicos/ServicoListParts";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
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
import { useFidelidadeLookups, useFidelidades } from "@/hooks/useFidelidade";
import type { Fidelidade } from "@/types/fidelidade";

export function FidelidadeList() {
  const fidelidadesQuery = useFidelidades();
  const lookupsQuery = useFidelidadeLookups();
  const searchParams = useSearchParams();
  const saved = searchParams.get("salvo") === "1";
  const fidelidades = fidelidadesQuery.data ?? [];
  const ativas = fidelidades.filter((item) => item.ativo).length;

  return (
    <section className="space-y-5">
      <FidelidadeHeader saved={saved} />
      <div className="grid gap-4 md:grid-cols-2">
        <SummaryCard
          title="Regras cadastradas"
          value={String(fidelidades.length)}
          description="Total de regras de fidelidade"
          icon={Star}
        />
        <SummaryCard
          title="Regras ativas"
          value={String(ativas)}
          description="Concedendo pontos atualmente"
          icon={Star}
        />
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Regras</CardTitle>
        </CardHeader>
        <CardContent>
          {fidelidadesQuery.isError || lookupsQuery.isError ? (
            <Alert variant="destructive">
              <AlertTitle>Erro ao carregar regras de fidelidade</AlertTitle>
              <AlertDescription>
                {fidelidadesQuery.error?.message ?? lookupsQuery.error?.message}
              </AlertDescription>
            </Alert>
          ) : (
            <FidelidadeTable
              isLoading={fidelidadesQuery.isLoading || lookupsQuery.isLoading}
              fidelidades={fidelidades}
              lookups={lookupsQuery.data}
            />
          )}
        </CardContent>
      </Card>
    </section>
  );
}

function FidelidadeHeader({ saved }: { saved: boolean }) {
  return (
    <>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Fidelidade</h1>
          <p className="text-muted-foreground text-sm">
            Regras de pontos concedidos por serviço ou produto.
          </p>
        </div>
        <Button asChild>
          <Link href="/fidelidade/nova">
            <Plus className="size-4" />
            Nova regra
          </Link>
        </Button>
      </div>
      {saved ? (
        <Alert>
          <AlertTitle>Regra salva com sucesso</AlertTitle>
          <AlertDescription>A lista foi atualizada.</AlertDescription>
        </Alert>
      ) : null}
    </>
  );
}

function FidelidadeTable({
  isLoading,
  fidelidades,
  lookups
}: {
  isLoading: boolean;
  fidelidades: Fidelidade[];
  lookups: ReturnType<typeof useFidelidadeLookups>["data"];
}) {
  if (isLoading) {
    return <Skeleton className="h-56 w-full" />;
  }

  if (fidelidades.length === 0) {
    return (
      <div className="text-muted-foreground flex min-h-40 items-center justify-center rounded-lg border text-sm">
        Nenhuma regra de fidelidade cadastrada
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Origem</TableHead>
            <TableHead>Item</TableHead>
            <TableHead>Pontos</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="text-right">Ações</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {fidelidades.map((fidelidade) => (
            <TableRow key={fidelidade.id_fidelidade}>
              <TableCell>
                <Badge variant="outline">{origemLabel(fidelidade)}</Badge>
              </TableCell>
              <TableCell>
                {lookups
                  ? origemNome(fidelidade, lookups.servicos, lookups.produtos)
                  : "—"}
              </TableCell>
              <TableCell>{fidelidade.pontos_acumulados} pts</TableCell>
              <TableCell>
                <Badge variant={fidelidade.ativo ? "secondary" : "outline"}>
                  {fidelidade.ativo ? "Ativa" : "Inativa"}
                </Badge>
              </TableCell>
              <TableCell className="text-right">
                <Button asChild variant="outline" size="sm">
                  <Link href={`/fidelidade/${fidelidade.id_fidelidade}/editar`}>
                    Editar
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
