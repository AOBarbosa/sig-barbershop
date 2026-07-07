"use client";

import type { LucideIcon } from "lucide-react";
import { MoreHorizontal } from "lucide-react";
import Link from "next/link";

import { formatCpf, formatDate } from "@/components/clientes/clienteFormatters";
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
import type { ClienteComPessoa } from "@/types/cliente";

function ClienteActions({ cliente }: { cliente: ClienteComPessoa }) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          aria-label={`Abrir ações do cliente ${cliente.pessoa.nome}`}>
          <MoreHorizontal className="size-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-40">
        <DropdownMenuLabel>Ações</DropdownMenuLabel>
        <DropdownMenuItem asChild>
          <Link href={`/clientes/${cliente.id_cliente}/editar`}>Editar</Link>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export function ClienteRow({ cliente }: { cliente: ClienteComPessoa }) {
  return (
    <TableRow>
      <TableCell className="font-medium">{cliente.pessoa.nome}</TableCell>
      <TableCell>{formatCpf(cliente.pessoa.cpf)}</TableCell>
      <TableCell className="text-muted-foreground">
        {cliente.pessoa.email ?? "—"}
      </TableCell>
      <TableCell>{formatDate(cliente.pessoa.data_nascimento)}</TableCell>
      <TableCell className="text-right">
        <ClienteActions cliente={cliente} />
      </TableCell>
    </TableRow>
  );
}

export function ClienteMobileCard({ cliente }: { cliente: ClienteComPessoa }) {
  return (
    <div className="rounded-lg border p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="font-medium">{cliente.pessoa.nome}</p>
          <p className="text-muted-foreground mt-1 text-sm">
            {formatCpf(cliente.pessoa.cpf)}
          </p>
        </div>
        <ClienteActions cliente={cliente} />
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <div>
          <p className="text-muted-foreground">Email</p>
          <p className="truncate font-medium">{cliente.pessoa.email ?? "—"}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Nascimento</p>
          <p className="font-medium">
            {formatDate(cliente.pessoa.data_nascimento)}
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
