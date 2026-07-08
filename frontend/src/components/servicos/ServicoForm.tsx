"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft, Loader2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useForm, useWatch } from "react-hook-form";

import {
  ServicoOperationalFields,
  ServicoPrimaryFields
} from "@/components/servicos/ServicoFormFields";
import {
  defaultServicoFormValues,
  servicoFormSchema,
  type ServicoFormInput,
  type ServicoFormValues
} from "@/components/servicos/servicoFormSchema";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Form } from "@/components/ui/form";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useCreateServico,
  useServico,
  useUpdateServico
} from "@/hooks/useServicos";
import type { ServicoPayload } from "@/types/servico";

export function ServicoForm({
  mode,
  servicoId
}: {
  mode: "create" | "edit";
  servicoId?: number;
}) {
  const router = useRouter();
  const createServico = useCreateServico();
  const updateServico = useUpdateServico(servicoId ?? 0);
  const servicoQuery = useServico(servicoId ?? Number.NaN);
  const form = useForm<ServicoFormInput, unknown, ServicoFormValues>({
    resolver: zodResolver(servicoFormSchema),
    defaultValues: defaultServicoFormValues
  });
  const ativo = Boolean(useWatch({ control: form.control, name: "ativo" }));
  const isEdit = mode === "edit";
  const isSubmitting = createServico.isPending || updateServico.isPending;
  const mutationError = createServico.error ?? updateServico.error;

  useEffect(() => {
    if (isEdit && servicoQuery.data) {
      form.reset({
        nome: servicoQuery.data.nome,
        preco: Number(servicoQuery.data.preco),
        duracao_em_minutos: servicoQuery.data.duracao_em_minutos,
        pontos_gerados: servicoQuery.data.pontos_gerados,
        ativo: servicoQuery.data.ativo
      });
    }
  }, [form, isEdit, servicoQuery.data]);

  async function onSubmit(values: ServicoFormValues) {
    const payload: ServicoPayload = { ...values };

    if (isEdit && servicoId) {
      await updateServico.mutateAsync(payload);
    } else {
      await createServico.mutateAsync(payload);
    }

    router.push("/servicos?salvo=1");
  }

  if (isEdit && servicoQuery.isLoading) {
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

  if (isEdit && servicoQuery.isError) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Serviço não carregado</AlertTitle>
        <AlertDescription>{servicoQuery.error.message}</AlertDescription>
      </Alert>
    );
  }

  return (
    <section className="mx-auto w-full max-w-5xl space-y-5">
      <Button asChild variant="ghost" className="px-0">
        <Link href="/servicos">
          <ArrowLeft className="size-4" />
          Voltar para serviços
        </Link>
      </Button>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
          <div className="grid gap-5 lg:grid-cols-[1fr_18rem]">
            <ServicoPrimaryFields form={form} isEdit={isEdit} />
            <ServicoOperationalFields form={form} ativo={ativo} />
          </div>
          {mutationError ? (
            <Alert variant="destructive">
              <AlertTitle>Erro ao salvar serviço</AlertTitle>
              <AlertDescription>{mutationError.message}</AlertDescription>
            </Alert>
          ) : null}
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button asChild variant="outline" type="button">
              <Link href="/servicos">Cancelar</Link>
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <Loader2 className="size-4 animate-spin" />
              ) : null}
              Salvar serviço
            </Button>
          </div>
        </form>
      </Form>
    </section>
  );
}
