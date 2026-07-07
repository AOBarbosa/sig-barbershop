"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft, Loader2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useForm } from "react-hook-form";

import {
  ClienteContactFields,
  ClientePrimaryFields
} from "@/components/clientes/ClienteFormFields";
import {
  clienteFormSchema,
  defaultClienteFormValues,
  type ClienteFormInput,
  type ClienteFormValues
} from "@/components/clientes/clienteFormSchema";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Form } from "@/components/ui/form";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useCliente,
  useCreateCliente,
  usePessoaDoCliente,
  useUpdateClientePessoa
} from "@/hooks/useClientes";
import type { PessoaPayload } from "@/types/cliente";

export function ClienteForm({
  mode,
  clienteId
}: {
  mode: "create" | "edit";
  clienteId?: number;
}) {
  const router = useRouter();
  const clienteQuery = useCliente(clienteId ?? Number.NaN);
  const pessoaQuery = usePessoaDoCliente(clienteQuery.data?.PESSOA_id_pessoa);
  const createCliente = useCreateCliente();
  const updatePessoa = useUpdateClientePessoa(
    clienteQuery.data?.PESSOA_id_pessoa ?? 0
  );
  const form = useForm<ClienteFormInput, unknown, ClienteFormValues>({
    resolver: zodResolver(clienteFormSchema),
    defaultValues: defaultClienteFormValues
  });
  const isEdit = mode === "edit";
  const isSubmitting = createCliente.isPending || updatePessoa.isPending;
  const mutationError = createCliente.error ?? updatePessoa.error;
  const isLoading = isEdit && (clienteQuery.isLoading || pessoaQuery.isLoading);
  const loadError = isEdit ? (clienteQuery.error ?? pessoaQuery.error) : null;

  useEffect(() => {
    if (isEdit && pessoaQuery.data) {
      form.reset({
        nome: pessoaQuery.data.nome,
        cpf: pessoaQuery.data.cpf,
        email: pessoaQuery.data.email ?? "",
        data_nascimento: pessoaQuery.data.data_nascimento ?? ""
      });
    }
  }, [form, isEdit, pessoaQuery.data]);

  async function onSubmit(values: ClienteFormValues) {
    const payload: PessoaPayload = { ...values };

    if (isEdit) {
      await updatePessoa.mutateAsync(payload);
    } else {
      await createCliente.mutateAsync(payload);
    }

    router.push("/clientes?salvo=1");
  }

  if (isLoading) {
    return (
      <div className="mx-auto w-full max-w-5xl space-y-5">
        <Skeleton className="h-9 w-40" />
        <div className="grid gap-5 lg:grid-cols-[1fr_18rem]">
          <Skeleton className="h-80 w-full" />
          <Skeleton className="h-48 w-full" />
        </div>
      </div>
    );
  }

  if (loadError) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Cliente não carregado</AlertTitle>
        <AlertDescription>{loadError.message}</AlertDescription>
      </Alert>
    );
  }

  return (
    <section className="mx-auto w-full max-w-5xl space-y-5">
      <Button asChild variant="ghost" className="px-0">
        <Link href="/clientes">
          <ArrowLeft className="size-4" />
          Voltar para clientes
        </Link>
      </Button>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
          <div className="grid gap-5 lg:grid-cols-[1fr_18rem]">
            <ClientePrimaryFields form={form} isEdit={isEdit} />
            <ClienteContactFields form={form} />
          </div>
          {mutationError ? (
            <Alert variant="destructive">
              <AlertTitle>Erro ao salvar cliente</AlertTitle>
              <AlertDescription>{mutationError.message}</AlertDescription>
            </Alert>
          ) : null}
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button asChild variant="outline" type="button">
              <Link href="/clientes">Cancelar</Link>
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <Loader2 className="size-4 animate-spin" />
              ) : null}
              Salvar cliente
            </Button>
          </div>
        </form>
      </Form>
    </section>
  );
}
