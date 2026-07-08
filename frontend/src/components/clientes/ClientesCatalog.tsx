"use client";

import { Search } from "lucide-react";
import Link from "next/link";

import {
  ClienteMobileCard,
  ClienteRow,
  LoadingRows
} from "@/components/clientes/ClienteListParts";
import { Button } from "@/components/ui/button";
import { CardDescription, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableHead,
  TableHeader,
  TableRow,
  TableCell
} from "@/components/ui/table";
import type { ClienteComPessoa } from "@/types/cliente";

export function CatalogToolbar({
  search,
  onSearchChange
}: {
  search: string;
  onSearchChange: (value: string) => void;
}) {
  return (
    <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
      <div>
        <CardTitle>Base de clientes</CardTitle>
        <CardDescription>
          Pessoas cadastradas como clientes da barbearia.
        </CardDescription>
      </div>
      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative">
          <Search className="text-muted-foreground absolute top-2.5 left-2.5 size-4" />
          <Input
            placeholder="Buscar cliente"
            value={search}
            onChange={(event) => onSearchChange(event.target.value)}
            className="w-full pl-8 sm:w-64"
          />
        </div>
      </div>
    </div>
  );
}

export function ClienteResults({
  isLoading,
  clientes
}: {
  isLoading: boolean;
  clientes: ClienteComPessoa[];
}) {
  return (
    <>
      <div className="hidden overflow-x-auto md:block">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nome</TableHead>
              <TableHead>CPF</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Nascimento</TableHead>
              <TableHead className="text-right">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? <LoadingRows /> : <DesktopRows clientes={clientes} />}
          </TableBody>
        </Table>
      </div>
      <MobileResults isLoading={isLoading} clientes={clientes} />
    </>
  );
}

function DesktopRows({ clientes }: { clientes: ClienteComPessoa[] }) {
  if (clientes.length === 0) {
    return <EmptyTableRow />;
  }

  return clientes.map((cliente) => (
    <ClienteRow key={cliente.PESSOA_id_pessoa} cliente={cliente} />
  ));
}

function EmptyTableRow() {
  return (
    <TableRow>
      <TableCell colSpan={5} className="text-muted-foreground h-32 text-center">
        <div className="flex flex-col items-center gap-3">
          <span>Nenhum cliente encontrado</span>
          <Button asChild variant="outline" size="sm">
            <Link href="/clientes/novo">Cadastrar cliente</Link>
          </Button>
        </div>
      </TableCell>
    </TableRow>
  );
}

function MobileResults({
  isLoading,
  clientes
}: {
  isLoading: boolean;
  clientes: ClienteComPessoa[];
}) {
  if (isLoading) {
    return (
      <div className="space-y-3 md:hidden" data-testid="clientes-mobile-list">
        {[1, 2, 3].map((row) => (
          <Skeleton key={row} className="h-32 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-3 md:hidden" data-testid="clientes-mobile-list">
      {clientes.length > 0 ? (
        clientes.map((cliente) => (
          <ClienteMobileCard key={cliente.PESSOA_id_pessoa} cliente={cliente} />
        ))
      ) : (
        <div className="text-muted-foreground flex min-h-40 flex-col items-center justify-center gap-3 rounded-lg border text-center text-sm">
          <span>Nenhum cliente encontrado</span>
          <Button asChild variant="outline" size="sm">
            <Link href="/clientes/novo">Cadastrar cliente</Link>
          </Button>
        </div>
      )}
    </div>
  );
}
