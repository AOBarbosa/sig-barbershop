"use client";

import type { LucideIcon } from "lucide-react";
import { MoreHorizontal } from "lucide-react";
import Link from "next/link";

import {
  formatCpf,
  formatDate
} from "@/components/barbeiros/barbeiroFormatters";
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

function formatComissao(comissao: string | null) {
  return comissao == null ? "—" : `${comissao}%`;
}

function BarbeiroActions({
  barbeiro,
  isAdmin
}: {
  barbeiro: BarbeiroComPessoa;
  isAdmin: boolean;
}) {
  if (!isAdmin) {
    return null;
  }

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
          <Link href={`/barbeiros/${barbeiro.PESSOA_id_pessoa}/editar`}>
            Editar
          </Link>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export function BarbeiroRow({
  barbeiro,
  isAdmin
}: {
  barbeiro: BarbeiroComPessoa;
  isAdmin: boolean;
}) {
  return (
    <TableRow>
      <TableCell className="font-medium">{barbeiro.pessoa.nome}</TableCell>
      <TableCell>{formatCpf(barbeiro.pessoa.cpf)}</TableCell>
      <TableCell className="text-muted-foreground">
        {barbeiro.apelido ?? "Sem apelido"}
      </TableCell>
      <TableCell>{formatComissao(barbeiro.comissao_percentual)}</TableCell>
      <TableCell>{formatDate(barbeiro.pessoa.data_nascimento)}</TableCell>
      <TableCell className="text-right">
        <BarbeiroActions barbeiro={barbeiro} isAdmin={isAdmin} />
      </TableCell>
    </TableRow>
  );
}

export function BarbeiroMobileCard({
  barbeiro,
  isAdmin
}: {
  barbeiro: BarbeiroComPessoa;
  isAdmin: boolean;
}) {
  return (
    <div className="rounded-lg border p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="font-medium">{barbeiro.pessoa.nome}</p>
          <p className="text-muted-foreground mt-1 text-sm">
            {barbeiro.apelido ?? "Sem apelido"}
          </p>
        </div>
        <BarbeiroActions barbeiro={barbeiro} isAdmin={isAdmin} />
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <div>
          <p className="text-muted-foreground">CPF</p>
          <p className="font-medium">{formatCpf(barbeiro.pessoa.cpf)}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Comissão</p>
          <p className="font-medium">
            {formatComissao(barbeiro.comissao_percentual)}
          </p>
        </div>
      </div>
    </div>
  );
}

export function LoadingRows() {
  return (
    <>
      {[1, 2, 3].map((row) => (
        <TableRow key={row}>
          <TableCell colSpan={5}>
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
