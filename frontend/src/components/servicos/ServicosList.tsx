"use client";

import { Clock, Plus, Scissors, Wallet } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";

import {
  CatalogToolbar,
  ServicoResults,
  type StatusFilter
} from "@/components/servicos/ServicosCatalog";
import { SummaryCard } from "@/components/servicos/ServicoListParts";
import {
  formatCurrency,
  getAveragePrice
} from "@/components/servicos/servicoFormatters";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { useServicos } from "@/hooks/useServicos";
import type { Servico } from "@/types/servico";

export function ServicosList() {
  const { data: servicos = [], isLoading, isError, error } = useServicos();
  const searchParams = useSearchParams();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("todos");
  const saved = searchParams.get("salvo") === "1";

  const activeCount = servicos.filter((servico) => servico.ativo).length;
  const filteredServicos = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase();

    return servicos.filter((servico) => {
      const matchesSearch =
        normalizedSearch.length === 0 ||
        servico.nome.toLowerCase().includes(normalizedSearch) ||
        (servico.descricao ?? "").toLowerCase().includes(normalizedSearch);
      const matchesStatus =
        statusFilter === "todos" ||
        (statusFilter === "ativos" && servico.ativo) ||
        (statusFilter === "inativos" && !servico.ativo);

      return matchesSearch && matchesStatus;
    });
  }, [search, servicos, statusFilter]);

  return (
    <section className="space-y-5">
      <ServicosHeader saved={saved} />
      <ServicosSummary servicos={servicos} active={activeCount} />
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
              <AlertTitle>Erro ao carregar serviços</AlertTitle>
              <AlertDescription>{error.message}</AlertDescription>
            </Alert>
          ) : (
            <ServicoResults isLoading={isLoading} servicos={filteredServicos} />
          )}
        </CardContent>
      </Card>
    </section>
  );
}

function ServicosHeader({ saved }: { saved: boolean }) {
  return (
    <>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Serviços</h1>
          <p className="text-muted-foreground text-sm">
            Catálogo de cortes, barba e serviços disponíveis.
          </p>
        </div>
        <Button asChild>
          <Link href="/servicos/novo">
            <Plus className="size-4" />
            Novo serviço
          </Link>
        </Button>
      </div>
      {saved ? (
        <Alert>
          <AlertTitle>Serviço salvo com sucesso</AlertTitle>
          <AlertDescription>
            A lista foi atualizada com as últimas informações.
          </AlertDescription>
        </Alert>
      ) : null}
    </>
  );
}

function ServicosSummary({
  servicos,
  active
}: {
  servicos: Servico[];
  active: number;
}) {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      <SummaryCard
        title="Total de serviços"
        value={String(servicos.length)}
        description="Itens cadastrados no catálogo"
        icon={Scissors}
      />
      <SummaryCard
        title="Serviços ativos"
        value={String(active)}
        description="Disponíveis para atendimento"
        icon={Clock}
      />
      <SummaryCard
        title="Preço médio"
        value={formatCurrency(getAveragePrice(servicos))}
        description="Média do catálogo atual"
        icon={Wallet}
      />
    </div>
  );
}
