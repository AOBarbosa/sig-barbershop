"use client";

import { Search } from "lucide-react";
import Link from "next/link";

import {
  LoadingRows,
  ServicoMobileCard,
  ServicoRow
} from "@/components/servicos/ServicoListParts";
import { Button } from "@/components/ui/button";
import { CardDescription, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from "@/components/ui/table";
import { cn } from "@/lib/utils";
import type { Servico } from "@/types/servico";

export type StatusFilter = "todos" | "ativos" | "inativos";

const filters = [
  { value: "todos", label: "Todos" },
  { value: "ativos", label: "Ativos" },
  { value: "inativos", label: "Inativos" }
] satisfies Array<{ value: StatusFilter; label: string }>;

export function CatalogToolbar({
  search,
  statusFilter,
  onSearchChange,
  onStatusChange
}: {
  search: string;
  statusFilter: StatusFilter;
  onSearchChange: (value: string) => void;
  onStatusChange: (value: StatusFilter) => void;
}) {
  return (
    <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
      <div>
        <CardTitle>Catálogo</CardTitle>
        <CardDescription>
          Preços usados como base nos atendimentos.
        </CardDescription>
      </div>
      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative">
          <Search className="text-muted-foreground absolute top-2.5 left-2.5 size-4" />
          <Input
            placeholder="Buscar serviço"
            value={search}
            onChange={(event) => onSearchChange(event.target.value)}
            className="w-full pl-8 sm:w-64"
          />
        </div>
        <div className="flex rounded-lg border p-1">
          {filters.map((filter) => (
            <Button
              key={filter.value}
              type="button"
              variant={statusFilter === filter.value ? "secondary" : "ghost"}
              size="sm"
              onClick={() => onStatusChange(filter.value)}
              className={cn(
                "h-7 px-2.5",
                statusFilter === filter.value && "shadow-sm"
              )}>
              {filter.label}
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
}

export function ServicoResults({
  isLoading,
  servicos
}: {
  isLoading: boolean;
  servicos: Servico[];
}) {
  return (
    <>
      <div className="hidden overflow-x-auto md:block">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nome</TableHead>
              <TableHead>Descrição</TableHead>
              <TableHead>Preço</TableHead>
              <TableHead>Duração</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? <LoadingRows /> : <DesktopRows servicos={servicos} />}
          </TableBody>
        </Table>
      </div>
      <MobileResults isLoading={isLoading} servicos={servicos} />
    </>
  );
}

function DesktopRows({ servicos }: { servicos: Servico[] }) {
  if (servicos.length === 0) {
    return <EmptyTableRow />;
  }

  return servicos.map((servico) => (
    <ServicoRow key={servico.id_servico} servico={servico} />
  ));
}

function EmptyTableRow() {
  return (
    <TableRow>
      <TableCell colSpan={6} className="text-muted-foreground h-32 text-center">
        <div className="flex flex-col items-center gap-3">
          <span>Nenhum serviço encontrado</span>
          <Button asChild variant="outline" size="sm">
            <Link href="/servicos/novo">Cadastrar serviço</Link>
          </Button>
        </div>
      </TableCell>
    </TableRow>
  );
}

function MobileResults({
  isLoading,
  servicos
}: {
  isLoading: boolean;
  servicos: Servico[];
}) {
  if (isLoading) {
    return (
      <div className="space-y-3 md:hidden" data-testid="servicos-mobile-list">
        {[1, 2, 3].map((row) => (
          <Skeleton key={row} className="h-36 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-3 md:hidden" data-testid="servicos-mobile-list">
      {servicos.length > 0 ? (
        servicos.map((servico) => (
          <ServicoMobileCard key={servico.id_servico} servico={servico} />
        ))
      ) : (
        <div className="text-muted-foreground flex min-h-40 flex-col items-center justify-center gap-3 rounded-lg border text-center text-sm">
          <span>Nenhum serviço encontrado</span>
          <Button asChild variant="outline" size="sm">
            <Link href="/servicos/novo">Cadastrar serviço</Link>
          </Button>
        </div>
      )}
    </div>
  );
}
