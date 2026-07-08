"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useForm, useWatch } from "react-hook-form";

import { FidelidadeFormActions } from "@/components/fidelidade/FidelidadeFormActions";
import { FidelidadeRuleFields } from "@/components/fidelidade/FidelidadeRuleFields";
import {
  defaultFidelidadeFormValues,
  fidelidadeFormSchema,
  type FidelidadeFormInput,
  type FidelidadeFormValues
} from "@/components/fidelidade/fidelidadeFormSchema";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from "@/components/ui/card";
import { Form } from "@/components/ui/form";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useCreateFidelidade,
  useFidelidadeItem,
  useFidelidadeLookups,
  useUpdateFidelidade
} from "@/hooks/useFidelidade";
import type { FidelidadePayload } from "@/types/fidelidade";

export function FidelidadeForm({
  mode,
  fidelidadeId
}: {
  mode: "create" | "edit";
  fidelidadeId?: number;
}) {
  const router = useRouter();
  const lookupsQuery = useFidelidadeLookups();
  const createFidelidade = useCreateFidelidade();
  const updateFidelidade = useUpdateFidelidade(fidelidadeId ?? 0);
  const fidelidadeQuery = useFidelidadeItem(fidelidadeId ?? Number.NaN);
  const isEdit = mode === "edit";
  const form = useForm<FidelidadeFormInput, unknown, FidelidadeFormValues>({
    resolver: zodResolver(fidelidadeFormSchema),
    defaultValues: defaultFidelidadeFormValues
  });
  const tipo = useWatch({ control: form.control, name: "tipo" });
  const ativo = Boolean(useWatch({ control: form.control, name: "ativo" }));
  const isSubmitting = createFidelidade.isPending || updateFidelidade.isPending;
  const mutationError = createFidelidade.error ?? updateFidelidade.error;

  useEffect(() => {
    if (isEdit && fidelidadeQuery.data) {
      const fidelidade = fidelidadeQuery.data;

      form.reset({
        tipo: fidelidade.SERVICO_id_servico ? "servico" : "produto",
        SERVICO_id_servico: fidelidade.SERVICO_id_servico ?? undefined,
        PRODUTO_id_produto: fidelidade.PRODUTO_id_produto ?? undefined,
        pontos: fidelidade.pontos_acumulados,
        ativo: fidelidade.ativo
      });
    }
  }, [form, isEdit, fidelidadeQuery.data]);

  async function onSubmit(values: FidelidadeFormValues) {
    const payload: FidelidadePayload = {
      SERVICO_id_servico:
        values.tipo === "servico" ? (values.SERVICO_id_servico ?? null) : null,
      PRODUTO_id_produto:
        values.tipo === "produto" ? (values.PRODUTO_id_produto ?? null) : null,
      pontos_acumulados: values.pontos,
      pontos_uso: 0,
      ativo: values.ativo
    };

    if (isEdit && fidelidadeId) {
      await updateFidelidade.mutateAsync(payload);
    } else {
      await createFidelidade.mutateAsync(payload);
    }

    router.push("/fidelidade?salvo=1");
  }

  if (lookupsQuery.isLoading || (isEdit && fidelidadeQuery.isLoading)) {
    return <Skeleton className="mx-auto h-96 w-full max-w-3xl" />;
  }

  if (lookupsQuery.isError || (isEdit && fidelidadeQuery.isError)) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Dados não carregados</AlertTitle>
        <AlertDescription>
          {lookupsQuery.error?.message ?? fidelidadeQuery.error?.message}
        </AlertDescription>
      </Alert>
    );
  }

  const lookups = lookupsQuery.data;

  if (!lookups) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Dados não encontrados</AlertTitle>
        <AlertDescription>
          Não foi possível montar o formulário de fidelidade.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <section className="mx-auto w-full max-w-3xl space-y-5">
      <Button asChild variant="ghost" className="px-0">
        <Link href="/fidelidade">
          <ArrowLeft className="size-4" />
          Voltar para fidelidade
        </Link>
      </Button>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="space-y-5"
          noValidate>
          <Card>
            <CardHeader>
              <CardTitle>
                {isEdit
                  ? "Editar regra de fidelidade"
                  : "Nova regra de fidelidade"}
              </CardTitle>
              <CardDescription>
                Escolha um serviço ou um produto — nunca os dois — e quantos
                pontos a regra gera.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              <FidelidadeRuleFields
                form={form}
                lookups={lookups}
                tipo={tipo}
                ativo={ativo}
              />
            </CardContent>
          </Card>
          {mutationError ? (
            <Alert variant="destructive">
              <AlertTitle>Erro ao salvar regra de fidelidade</AlertTitle>
              <AlertDescription>{mutationError.message}</AlertDescription>
            </Alert>
          ) : null}
          <FidelidadeFormActions loading={isSubmitting} />
        </form>
      </Form>
    </section>
  );
}
