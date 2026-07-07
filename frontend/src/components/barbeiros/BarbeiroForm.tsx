"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft, Loader2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useForm, useWatch } from "react-hook-form";

import {
  BarbeiroPrimaryFields,
  BarbeiroProfessionalFields
} from "@/components/barbeiros/BarbeiroFormFields";
import {
  barbeiroFormSchema,
  defaultBarbeiroFormValues,
  type BarbeiroFormInput,
  type BarbeiroFormValues
} from "@/components/barbeiros/barbeiroFormSchema";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Form } from "@/components/ui/form";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useBarbeiroComPessoa,
  useCreateBarbeiro,
  useUpdateBarbeiro
} from "@/hooks/useBarbeiros";
import type { BarbeiroFormPayload } from "@/types/barbeiro";

export function BarbeiroForm({
  mode,
  barbeiroId
}: {
  mode: "create" | "edit";
  barbeiroId?: number;
}) {
  const router = useRouter();
  const barbeiroQuery = useBarbeiroComPessoa(barbeiroId ?? Number.NaN);
  const createBarbeiro = useCreateBarbeiro();
  const updateBarbeiro = useUpdateBarbeiro(
    barbeiroId ?? 0,
    barbeiroQuery.data?.pessoa.id_pessoa ?? 0
  );
  const form = useForm<BarbeiroFormInput, unknown, BarbeiroFormValues>({
    resolver: zodResolver(barbeiroFormSchema),
    defaultValues: defaultBarbeiroFormValues
  });
  const ativo = Boolean(useWatch({ control: form.control, name: "ativo" }));
  const isEdit = mode === "edit";
  const isSubmitting = createBarbeiro.isPending || updateBarbeiro.isPending;
  const mutationError = createBarbeiro.error ?? updateBarbeiro.error;

  useEffect(() => {
    if (isEdit && barbeiroQuery.data) {
      const { barbeiro, pessoa } = barbeiroQuery.data;
      form.reset({
        nome: pessoa.nome,
        cpf: pessoa.cpf,
        email: pessoa.email ?? "",
        data_nascimento: pessoa.data_nascimento ?? "",
        especialidade: barbeiro.especialidade ?? "",
        ativo: barbeiro.ativo
      });
    }
  }, [form, isEdit, barbeiroQuery.data]);

  async function onSubmit(values: BarbeiroFormValues) {
    const payload: BarbeiroFormPayload = { ...values };

    try {
      if (isEdit) {
        await updateBarbeiro.mutateAsync(payload);
      } else {
        await createBarbeiro.mutateAsync(payload);
      }
      router.push("/barbeiros?salvo=1");
    } catch {
      // erro já exibido via mutationError
    }
  }

  if (isEdit && barbeiroQuery.isLoading) {
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

  if (isEdit && barbeiroQuery.isError) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Barbeiro não carregado</AlertTitle>
        <AlertDescription>{barbeiroQuery.error.message}</AlertDescription>
      </Alert>
    );
  }

  return (
    <section className="mx-auto w-full max-w-5xl space-y-5">
      <Button asChild variant="ghost" className="px-0">
        <Link href="/barbeiros">
          <ArrowLeft className="size-4" />
          Voltar para barbeiros
        </Link>
      </Button>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="space-y-5"
          noValidate>
          <div className="grid gap-5 lg:grid-cols-[1fr_18rem]">
            <BarbeiroPrimaryFields form={form} isEdit={isEdit} />
            <BarbeiroProfessionalFields form={form} ativo={ativo} />
          </div>
          {mutationError ? (
            <Alert variant="destructive">
              <AlertTitle>Erro ao salvar barbeiro</AlertTitle>
              <AlertDescription>{mutationError.message}</AlertDescription>
            </Alert>
          ) : null}
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button asChild variant="outline" type="button">
              <Link href="/barbeiros">Cancelar</Link>
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <Loader2 className="size-4 animate-spin" />
              ) : null}
              Salvar barbeiro
            </Button>
          </div>
        </form>
      </Form>
    </section>
  );
}
