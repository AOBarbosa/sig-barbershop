"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft, Loader2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useForm, useWatch } from "react-hook-form";

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
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Skeleton } from "@/components/ui/skeleton";
import { Switch } from "@/components/ui/switch";
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
        pontos: fidelidade.pontos,
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
      pontos: values.pontos,
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
              <FormItem>
                <FormLabel>Aplicar regra a</FormLabel>
                <RadioGroup
                  value={tipo}
                  onValueChange={(value) =>
                    form.setValue("tipo", value as "servico" | "produto", {
                      shouldDirty: true,
                      shouldValidate: true
                    })
                  }
                  className="grid grid-cols-2 gap-3">
                  <label className="flex cursor-pointer items-center gap-2 rounded-lg border p-3 text-sm">
                    <RadioGroupItem value="servico" />
                    Serviço
                  </label>
                  <label className="flex cursor-pointer items-center gap-2 rounded-lg border p-3 text-sm">
                    <RadioGroupItem value="produto" />
                    Produto
                  </label>
                </RadioGroup>
                <FormMessage>{form.formState.errors.tipo?.message}</FormMessage>
              </FormItem>
              {tipo === "servico" ? (
                <FormField name="SERVICO_id_servico">
                  {(field) => (
                    <FormItem>
                      <FormLabel htmlFor="servico">Serviço</FormLabel>
                      <FormControl>
                        <select
                          id="servico"
                          className="h-10 w-full rounded-lg border px-3 text-sm"
                          {...field}>
                          <option value="">Selecione</option>
                          {lookups.servicos
                            .filter((servico) => servico.ativo)
                            .map((servico) => (
                              <option
                                key={servico.id_servico}
                                value={servico.id_servico}>
                                {servico.nome}
                              </option>
                            ))}
                        </select>
                      </FormControl>
                    </FormItem>
                  )}
                </FormField>
              ) : (
                <FormField name="PRODUTO_id_produto">
                  {(field) => (
                    <FormItem>
                      <FormLabel htmlFor="produto">Produto</FormLabel>
                      <FormControl>
                        <select
                          id="produto"
                          className="h-10 w-full rounded-lg border px-3 text-sm"
                          {...field}>
                          <option value="">Selecione</option>
                          {lookups.produtos
                            .filter((produto) => produto.ativo)
                            .map((produto) => (
                              <option
                                key={produto.id_produto}
                                value={produto.id_produto}>
                                {produto.nome}
                              </option>
                            ))}
                        </select>
                      </FormControl>
                    </FormItem>
                  )}
                </FormField>
              )}
              <FormField name="pontos">
                {(field) => (
                  <FormItem>
                    <FormLabel htmlFor="pontos">Pontos</FormLabel>
                    <FormControl>
                      <Input
                        id="pontos"
                        type="number"
                        min="1"
                        step="1"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage>
                      {form.formState.errors.pontos?.message}
                    </FormMessage>
                  </FormItem>
                )}
              </FormField>
              <FormItem>
                <div className="flex items-center justify-between rounded-lg border p-3">
                  <div className="space-y-1">
                    <FormLabel htmlFor="ativo">Regra ativa</FormLabel>
                    <p className="text-muted-foreground text-sm">
                      {ativo
                        ? "Pontos são concedidos nas próximas vendas/atendimentos"
                        : "Regra desativada, não concede mais pontos"}
                    </p>
                  </div>
                  <Switch
                    id="ativo"
                    checked={ativo}
                    onCheckedChange={(checked) =>
                      form.setValue("ativo", checked, {
                        shouldDirty: true,
                        shouldValidate: true
                      })
                    }
                  />
                </div>
              </FormItem>
            </CardContent>
          </Card>
          {mutationError ? (
            <Alert variant="destructive">
              <AlertTitle>Erro ao salvar regra de fidelidade</AlertTitle>
              <AlertDescription>{mutationError.message}</AlertDescription>
            </Alert>
          ) : null}
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button asChild variant="outline" type="button">
              <Link href="/fidelidade">Cancelar</Link>
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <Loader2 className="size-4 animate-spin" />
              ) : null}
              Salvar regra
            </Button>
          </div>
        </form>
      </Form>
    </section>
  );
}
