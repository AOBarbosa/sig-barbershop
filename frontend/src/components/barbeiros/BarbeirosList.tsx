"use client";

import { Award, Plus, Scissors, UserCheck } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";

import {
  BarbeiroResults,
  CatalogToolbar,
  type StatusFilter
} from "@/components/barbeiros/BarbeirosCatalog";
import {
  getBarbeirosAtivos,
  getEspecialidadesUnicas
} from "@/components/barbeiros/barbeiroFormatters";
import { SummaryCard } from "@/components/barbeiros/BarbeiroListParts";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { useBarbeiros } from "@/hooks/useBarbeiros";
import type { BarbeiroComPessoa } from "@/types/barbeiro";

export function BarbeirosList() {
  const { data: barbeiros = [], isLoading, isError, error } = useBarbeiros();
  const searchParams = useSearchParams();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("todos");
  const saved = searchParams.get("salvo") === "1";

  const ativos = getBarbeirosAtivos(barbeiros);
  const especialidades = getEspecialidadesUnicas(barbeiros);
  const filteredBarbeiros = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase();

    return barbeiros.filter((barbeiro) => {
      const matchesSearch =
        normalizedSearch.length === 0 ||
        barbeiro.pessoa.nome.toLowerCase().includes(normalizedSearch) ||
        (barbeiro.especialidade ?? "").toLowerCase().includes(normalizedSearch);
      const matchesStatus =
        statusFilter === "todos" ||
        (statusFilter === "ativos" && barbeiro.ativo) ||
        (statusFilter === "inativos" && !barbeiro.ativo);

      return matchesSearch && matchesStatus;
    });
  }, [barbeiros, search, statusFilter]);

  return (
    <section className="space-y-5">
      <BarbeirosHeader saved={saved} />
      <BarbeirosSummary
        barbeiros={barbeiros}
        ativos={ativos}
        especialidades={especialidades}
      />
      <Card>
        <CardHeader>
          <CatalogToolbar
            search={search}
            statusFilter={statusFilter}
            onSearchChange={setSearch}
            onStatusChange={setStatusFilter}
          />
        </CardHeader>
        <CardContent>
          {isError ? (
            <Alert variant="destructive">
              <AlertTitle>Erro ao carregar barbeiros</AlertTitle>
              <AlertDescription>{error.message}</AlertDescription>
            </Alert>
          ) : (
            <BarbeiroResults
              isLoading={isLoading}
              barbeiros={filteredBarbeiros}
            />
          )}
        </CardContent>
      </Card>
    </section>
  );
}

function BarbeirosHeader({ saved }: { saved: boolean }) {
  return (
    <>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Barbeiros</h1>
          <p className="text-muted-foreground text-sm">
            Equipe de profissionais e suas especialidades.
          </p>
        </div>
        <Button asChild>
          <Link href="/barbeiros/novo">
            <Plus className="size-4" />
            Novo barbeiro
          </Link>
        </Button>
      </div>
      {saved ? (
        <Alert>
          <AlertTitle>Barbeiro salvo com sucesso</AlertTitle>
          <AlertDescription>
            A lista foi atualizada com as últimas informações.
          </AlertDescription>
        </Alert>
      ) : null}
    </>
  );
}

function BarbeirosSummary({
  barbeiros,
  ativos,
  especialidades
}: {
  barbeiros: BarbeiroComPessoa[];
  ativos: number;
  especialidades: number;
}) {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      <SummaryCard
        title="Total de barbeiros"
        value={String(barbeiros.length)}
        description="Profissionais cadastrados"
        icon={Scissors}
      />
      <SummaryCard
        title="Barbeiros ativos"
        value={String(ativos)}
        description="Disponíveis para atendimento"
        icon={UserCheck}
      />
      <SummaryCard
        title="Especialidades"
        value={String(especialidades)}
        description="Diferentes áreas de atuação"
        icon={Award}
      />
    </div>
  );
}
