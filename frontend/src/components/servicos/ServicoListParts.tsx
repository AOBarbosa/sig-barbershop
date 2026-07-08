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
import { formatCurrency } from "@/components/servicos/servicoFormatters";
import type { Servico } from "@/types/servico";

function ServicoActions({ servico }: { servico: Servico }) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          aria-label={`Abrir ações do serviço ${servico.nome}`}>
          <MoreHorizontal className="size-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-40">
        <DropdownMenuLabel>Ações</DropdownMenuLabel>
        <DropdownMenuItem asChild>
          <Link href={`/servicos/${servico.id_servico}/editar`}>Editar</Link>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export function ServicoRow({ servico }: { servico: Servico }) {
  return (
    <TableRow>
      <TableCell className="font-medium">{servico.nome}</TableCell>
      <TableCell>{formatCurrency(servico.preco)}</TableCell>
      <TableCell>{servico.duracao_em_minutos} min</TableCell>
      <TableCell>{servico.pontos_gerados}</TableCell>
      <TableCell>
        <Badge variant={servico.ativo ? "secondary" : "outline"}>
          {servico.ativo ? "Ativo" : "Inativo"}
        </Badge>
      </TableCell>
      <TableCell className="text-right">
        <ServicoActions servico={servico} />
      </TableCell>
    </TableRow>
  );
}

export function ServicoMobileCard({ servico }: { servico: Servico }) {
  return (
    <div className="rounded-lg border p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="font-medium">{servico.nome}</p>
        </div>
        <ServicoActions servico={servico} />
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <div>
          <p className="text-muted-foreground">Preço</p>
          <p className="font-medium">{formatCurrency(servico.preco)}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Duração</p>
          <p className="font-medium">{servico.duracao_em_minutos} min</p>
        </div>
        <div>
          <p className="text-muted-foreground">Pontos</p>
          <p className="font-medium">{servico.pontos_gerados}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Status</p>
          <p className="font-medium">{servico.ativo ? "Ativo" : "Inativo"}</p>
        </div>
      </div>
      <Badge className="mt-4" variant={servico.ativo ? "secondary" : "outline"}>
        {servico.ativo ? "Ativo" : "Inativo"}
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
