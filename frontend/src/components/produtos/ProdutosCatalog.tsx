"use client";

import { Search } from "lucide-react";
import Link from "next/link";

import {
  LoadingRows,
  ProdutoMobileCard,
  ProdutoRow
} from "@/components/produtos/ProdutoListParts";
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
import type { Produto } from "@/types/produto";

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
          Produtos disponíveis para venda no balcão.
        </CardDescription>
      </div>
      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative">
          <Search className="text-muted-foreground absolute top-2.5 left-2.5 size-4" />
          <Input
            placeholder="Buscar produto"
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

export function ProdutoResults({
  isLoading,
  produtos
}: {
  isLoading: boolean;
  produtos: Produto[];
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
              <TableHead>Estoque</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? <LoadingRows /> : <DesktopRows produtos={produtos} />}
          </TableBody>
        </Table>
      </div>
      <MobileResults isLoading={isLoading} produtos={produtos} />
    </>
  );
}

function DesktopRows({ produtos }: { produtos: Produto[] }) {
  if (produtos.length === 0) {
    return <EmptyTableRow />;
  }

  return produtos.map((produto) => (
    <ProdutoRow key={produto.id_produto} produto={produto} />
  ));
}

function EmptyTableRow() {
  return (
    <TableRow>
      <TableCell colSpan={6} className="text-muted-foreground h-32 text-center">
        <div className="flex flex-col items-center gap-3">
          <span>Nenhum produto encontrado</span>
          <Button asChild variant="outline" size="sm">
            <Link href="/produtos/novo">Cadastrar produto</Link>
          </Button>
        </div>
      </TableCell>
    </TableRow>
  );
}

function MobileResults({
  isLoading,
  produtos
}: {
  isLoading: boolean;
  produtos: Produto[];
}) {
  if (isLoading) {
    return (
      <div className="space-y-3 md:hidden" data-testid="produtos-mobile-list">
        {[1, 2, 3].map((row) => (
          <Skeleton key={row} className="h-36 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-3 md:hidden" data-testid="produtos-mobile-list">
      {produtos.length > 0 ? (
        produtos.map((produto) => (
          <ProdutoMobileCard key={produto.id_produto} produto={produto} />
        ))
      ) : (
        <div className="text-muted-foreground flex min-h-40 flex-col items-center justify-center gap-3 rounded-lg border text-center text-sm">
          <span>Nenhum produto encontrado</span>
          <Button asChild variant="outline" size="sm">
            <Link href="/produtos/novo">Cadastrar produto</Link>
          </Button>
        </div>
      )}
    </div>
  );
}
