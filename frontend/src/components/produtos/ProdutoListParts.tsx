"use client";

import type { LucideIcon } from "lucide-react";
import { MoreHorizontal } from "lucide-react";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger
} from "@/components/ui/dropdown-menu";
import { Skeleton } from "@/components/ui/skeleton";
import { TableCell, TableRow } from "@/components/ui/table";
import { formatCurrency } from "@/components/produtos/produtoFormatters";
import type { Produto } from "@/types/produto";

function ProdutoActions({ produto }: { produto: Produto }) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          aria-label={`Abrir ações do produto ${produto.nome}`}>
          <MoreHorizontal className="size-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-40">
        <DropdownMenuLabel>Ações</DropdownMenuLabel>
        <DropdownMenuItem asChild>
          <Link href={`/produtos/${produto.id_produto}/editar`}>Editar</Link>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export function ProdutoRow({ produto }: { produto: Produto }) {
  return (
    <TableRow>
      <TableCell className="font-medium">{produto.nome}</TableCell>
      <TableCell className="text-muted-foreground">
        {produto.descricao || "Sem descrição"}
      </TableCell>
      <TableCell>{formatCurrency(produto.preco)}</TableCell>
      <TableCell>{produto.estoque} un.</TableCell>
      <TableCell>
        <Badge variant={produto.ativo ? "secondary" : "outline"}>
          {produto.ativo ? "Ativo" : "Inativo"}
        </Badge>
      </TableCell>
      <TableCell className="text-right">
        <ProdutoActions produto={produto} />
      </TableCell>
    </TableRow>
  );
}

export function ProdutoMobileCard({ produto }: { produto: Produto }) {
  return (
    <div className="rounded-lg border p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="font-medium">{produto.nome}</p>
          <p className="text-muted-foreground mt-1 text-sm">
            {produto.descricao || "Sem descrição"}
          </p>
        </div>
        <ProdutoActions produto={produto} />
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <div>
          <p className="text-muted-foreground">Preço</p>
          <p className="font-medium">{formatCurrency(produto.preco)}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Estoque</p>
          <p className="font-medium">{produto.estoque} un.</p>
        </div>
      </div>
      <Badge className="mt-4" variant={produto.ativo ? "secondary" : "outline"}>
        {produto.ativo ? "Ativo" : "Inativo"}
      </Badge>
    </div>
  );
}

export function LoadingRows() {
  return (
    <>
      {[1, 2, 3].map((row) => (
        <TableRow key={row}>
          <TableCell colSpan={6}>
            <Skeleton className="h-8 w-full" />
          </TableCell>
        </TableRow>
      ))}
    </>
  );
}

export function SummaryCard({
  title,
  value,
  description,
  icon: Icon
}: {
  title: string;
  value: string;
  description: string;
  icon: LucideIcon;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between gap-3 space-y-0">
        <div>
          <CardDescription>{title}</CardDescription>
          <CardTitle className="text-2xl">{value}</CardTitle>
        </div>
        <div className="bg-muted flex size-9 items-center justify-center rounded-lg">
          <Icon className="size-4" />
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground text-sm">{description}</p>
      </CardContent>
    </Card>
  );
}
