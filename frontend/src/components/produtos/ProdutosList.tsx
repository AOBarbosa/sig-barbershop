"use client";

import { Layers, Package, PackageCheck, Plus } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";

import {
  CatalogToolbar,
  ProdutoResults,
  type StatusFilter
} from "@/components/produtos/ProdutosCatalog";
import { SummaryCard } from "@/components/produtos/ProdutoListParts";
import { getCategoriasCount } from "@/components/produtos/produtoFormatters";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { useProdutos } from "@/hooks/useProdutos";
import type { Produto } from "@/types/produto";

export function ProdutosList() {
  const { data: produtos = [], isLoading, isError, error } = useProdutos();
  const searchParams = useSearchParams();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("todos");
  const saved = searchParams.get("salvo") === "1";

  const activeCount = produtos.filter((produto) => produto.ativo).length;
  const filteredProdutos = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase();

    return produtos.filter((produto) => {
      const matchesSearch =
        normalizedSearch.length === 0 ||
        produto.nome.toLowerCase().includes(normalizedSearch) ||
        (produto.categoria ?? "").toLowerCase().includes(normalizedSearch);
      const matchesStatus =
        statusFilter === "todos" ||
        (statusFilter === "ativos" && produto.ativo) ||
        (statusFilter === "inativos" && !produto.ativo);

      return matchesSearch && matchesStatus;
    });
  }, [search, produtos, statusFilter]);

  return (
    <section className="space-y-5">
      <ProdutosHeader saved={saved} />
      <ProdutosSummary produtos={produtos} active={activeCount} />
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
              <AlertTitle>Erro ao carregar produtos</AlertTitle>
              <AlertDescription>{error.message}</AlertDescription>
            </Alert>
          ) : (
            <ProdutoResults isLoading={isLoading} produtos={filteredProdutos} />
          )}
        </CardContent>
      </Card>
    </section>
  );
}

function ProdutosHeader({ saved }: { saved: boolean }) {
  return (
    <>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Produtos</h1>
          <p className="text-muted-foreground text-sm">
            Catálogo de produtos disponíveis para venda.
          </p>
        </div>
        <Button asChild>
          <Link href="/produtos/novo">
            <Plus className="size-4" />
            Novo produto
          </Link>
        </Button>
      </div>
      {saved ? (
        <Alert>
          <AlertTitle>Produto salvo com sucesso</AlertTitle>
          <AlertDescription>
            A lista foi atualizada com as últimas informações.
          </AlertDescription>
        </Alert>
      ) : null}
    </>
  );
}

function ProdutosSummary({
  produtos,
  active
}: {
  produtos: Produto[];
  active: number;
}) {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      <SummaryCard
        title="Total de produtos"
        value={String(produtos.length)}
        description="Itens cadastrados no catálogo"
        icon={Package}
      />
      <SummaryCard
        title="Produtos ativos"
        value={String(active)}
        description="Disponíveis para venda"
        icon={PackageCheck}
      />
      <SummaryCard
        title="Categorias"
        value={String(getCategoriasCount(produtos))}
        description="Grupos distintos no catálogo"
        icon={Layers}
      />
    </div>
  );
}
