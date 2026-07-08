"use client";

import { BadgePercent, Plus, Scissors, UserRoundCheck } from "lucide-react";
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
import { useAuth } from "@/hooks/useAuth";
import { useBarbeiros } from "@/hooks/useBarbeiros";
import type { BarbeiroComPessoa } from "@/types/barbeiro";

export function BarbeirosList() {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";
  const { data: barbeiros = [], isLoading, isError, error } = useBarbeiros();
  const searchParams = useSearchParams();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("todos");
  const saved = searchParams.get("salvo") === "1";

  const cadastrados = getBarbeirosAtivos(barbeiros);
  const apelidos = getEspecialidadesUnicas(barbeiros);
  const filteredBarbeiros = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase();

    return barbeiros.filter((barbeiro) => {
      const matchesSearch =
        normalizedSearch.length === 0 ||
        barbeiro.pessoa.nome.toLowerCase().includes(normalizedSearch) ||
        (barbeiro.apelido ?? "").toLowerCase().includes(normalizedSearch);

      return matchesSearch;
    });
  }, [barbeiros, search]);

  return (
    <section className="space-y-5">
      <BarbeirosHeader saved={saved} isAdmin={isAdmin} />
      <BarbeirosSummary
        barbeiros={barbeiros}
        cadastrados={cadastrados}
        apelidos={apelidos}
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
              isAdmin={isAdmin}
            />
          )}
        </CardContent>
      </Card>
    </section>
  );
}

function BarbeirosHeader({
  saved,
  isAdmin
}: {
  saved: boolean;
  isAdmin: boolean;
}) {
  return (
    <>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Barbeiros</h1>
          <p className="text-muted-foreground text-sm">
            Equipe de profissionais e suas comissões.
          </p>
        </div>
        {isAdmin ? (
          <Button asChild>
            <Link href="/barbeiros/novo">
              <Plus className="size-4" />
              Novo barbeiro
            </Link>
          </Button>
        ) : null}
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
  cadastrados,
  apelidos
}: {
  barbeiros: BarbeiroComPessoa[];
  cadastrados: number;
  apelidos: number;
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
        title="Barbeiros cadastrados"
        value={String(cadastrados)}
        description="Vinculados a pessoas"
        icon={UserRoundCheck}
      />
      <SummaryCard
        title="Apelidos"
        value={String(apelidos)}
        description="Identificações profissionais"
        icon={BadgePercent}
      />
    </div>
  );
}
