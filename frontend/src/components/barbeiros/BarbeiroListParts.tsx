"use client";

import type { LucideIcon } from "lucide-react";
import { MoreHorizontal } from "lucide-react";
import Link from "next/link";

import {
  formatCpf,
  formatDate
} from "@/components/barbeiros/barbeiroFormatters";
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
import type { BarbeiroComPessoa } from "@/types/barbeiro";

function BarbeiroActions({ barbeiro }: { barbeiro: BarbeiroComPessoa }) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          aria-label={`Abrir ações do barbeiro ${barbeiro.pessoa.nome}`}>
          <MoreHorizontal className="size-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-40">
        <DropdownMenuLabel>Ações</DropdownMenuLabel>
        <DropdownMenuItem asChild>
          <Link href={`/barbeiros/${barbeiro.id_barbeiro}/editar`}>Editar</Link>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export function BarbeiroRow({ barbeiro }: { barbeiro: BarbeiroComPessoa }) {
  return (
    <TableRow>
      <TableCell className="font-medium">{barbeiro.pessoa.nome}</TableCell>
      <TableCell>{formatCpf(barbeiro.pessoa.cpf)}</TableCell>
      <TableCell className="text-muted-foreground">
        {barbeiro.especialidade ?? "Sem especialidade"}
      </TableCell>
      <TableCell>{formatDate(barbeiro.pessoa.data_nascimento)}</TableCell>
      <TableCell>
        <Badge variant={barbeiro.ativo ? "secondary" : "outline"}>
          {barbeiro.ativo ? "Ativo" : "Inativo"}
        </Badge>
      </TableCell>
      <TableCell className="text-right">
        <BarbeiroActions barbeiro={barbeiro} />
      </TableCell>
    </TableRow>
  );
}

export function BarbeiroMobileCard({
  barbeiro
}: {
  barbeiro: BarbeiroComPessoa;
}) {
  return (
    <div className="rounded-lg border p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="font-medium">{barbeiro.pessoa.nome}</p>
          <p className="text-muted-foreground mt-1 text-sm">
            {barbeiro.especialidade ?? "Sem especialidade"}
          </p>
        </div>
        <BarbeiroActions barbeiro={barbeiro} />
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <div>
          <p className="text-muted-foreground">CPF</p>
          <p className="font-medium">{formatCpf(barbeiro.pessoa.cpf)}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Nascimento</p>
          <p className="font-medium">
            {formatDate(barbeiro.pessoa.data_nascimento)}
          </p>
        </div>
      </div>
      <Badge
        className="mt-4"
        variant={barbeiro.ativo ? "secondary" : "outline"}>
        {barbeiro.ativo ? "Ativo" : "Inativo"}
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
