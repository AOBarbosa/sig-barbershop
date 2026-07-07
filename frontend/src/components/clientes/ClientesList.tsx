"use client";

import { Mail, Plus, UserCheck, Users } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";

import {
  CatalogToolbar,
  ClienteResults
} from "@/components/clientes/ClientesCatalog";
import { getClientesComEmail } from "@/components/clientes/clienteFormatters";
import { SummaryCard } from "@/components/clientes/ClienteListParts";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { useClientes } from "@/hooks/useClientes";
import type { ClienteComPessoa } from "@/types/cliente";

export function ClientesList() {
  const { data: clientes = [], isLoading, isError, error } = useClientes();
  const searchParams = useSearchParams();
  const [search, setSearch] = useState("");
  const saved = searchParams.get("salvo") === "1";

  const clientesComEmail = getClientesComEmail(clientes);
  const filteredClientes = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase();

    if (normalizedSearch.length === 0) {
      return clientes;
    }

    return clientes.filter((cliente) => {
      return (
        cliente.pessoa.nome.toLowerCase().includes(normalizedSearch) ||
        cliente.pessoa.cpf.includes(normalizedSearch) ||
        (cliente.pessoa.email ?? "").toLowerCase().includes(normalizedSearch)
      );
    });
  }, [clientes, search]);

  return (
    <section className="space-y-5">
      <ClientesHeader saved={saved} />
      <ClientesSummary
        clientes={clientes}
        clientesComEmail={clientesComEmail}
      />
      <Card>
        <CardHeader>
          <CatalogToolbar search={search} onSearchChange={setSearch} />
        </CardHeader>
        <CardContent>
          {isError ? (
            <Alert variant="destructive">
              <AlertTitle>Erro ao carregar clientes</AlertTitle>
              <AlertDescription>{error.message}</AlertDescription>
            </Alert>
          ) : (
            <ClienteResults isLoading={isLoading} clientes={filteredClientes} />
          )}
        </CardContent>
      </Card>
    </section>
  );
}

function ClientesHeader({ saved }: { saved: boolean }) {
  return (
    <>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Clientes</h1>
          <p className="text-muted-foreground text-sm">
            Cadastro de clientes atendidos pela barbearia.
          </p>
        </div>
        <Button asChild>
          <Link href="/clientes/novo">
            <Plus className="size-4" />
            Novo cliente
          </Link>
        </Button>
      </div>
      {saved ? (
        <Alert>
          <AlertTitle>Cliente salvo com sucesso</AlertTitle>
          <AlertDescription>
            A lista foi atualizada com as últimas informações.
          </AlertDescription>
        </Alert>
      ) : null}
    </>
  );
}

function ClientesSummary({
  clientes,
  clientesComEmail
}: {
  clientes: ClienteComPessoa[];
  clientesComEmail: number;
}) {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      <SummaryCard
        title="Total de clientes"
        value={String(clientes.length)}
        description="Pessoas cadastradas como clientes"
        icon={Users}
      />
      <SummaryCard
        title="Com email"
        value={String(clientesComEmail)}
        description="Contatáveis por email"
        icon={Mail}
      />
      <SummaryCard
        title="Cadastro ativo"
        value={String(clientes.length)}
        description="Todos os clientes atuais"
        icon={UserCheck}
      />
    </div>
  );
}
