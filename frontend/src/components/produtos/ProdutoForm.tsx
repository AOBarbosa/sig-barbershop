"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft, Loader2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useForm, useWatch } from "react-hook-form";

import {
  ProdutoOperationalFields,
  ProdutoPrimaryFields
} from "@/components/produtos/ProdutoFormFields";
import {
  defaultProdutoFormValues,
  produtoFormSchema,
  type ProdutoFormInput,
  type ProdutoFormValues
} from "@/components/produtos/produtoFormSchema";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Form } from "@/components/ui/form";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useCreateProduto,
  useProduto,
  useUpdateProduto
} from "@/hooks/useProdutos";
import type { ProdutoPayload } from "@/types/produto";

export function ProdutoForm({
  mode,
  produtoId
}: {
  mode: "create" | "edit";
  produtoId?: number;
}) {
  const router = useRouter();
  const createProduto = useCreateProduto();
  const updateProduto = useUpdateProduto(produtoId ?? 0);
  const produtoQuery = useProduto(produtoId ?? Number.NaN);
  const form = useForm<ProdutoFormInput, unknown, ProdutoFormValues>({
    resolver: zodResolver(produtoFormSchema),
    defaultValues: defaultProdutoFormValues
  });
  const preco = Number(useWatch({ control: form.control, name: "preco" }) || 0);
  const ativo = Boolean(useWatch({ control: form.control, name: "ativo" }));
  const isEdit = mode === "edit";
  const isSubmitting = createProduto.isPending || updateProduto.isPending;
  const mutationError = createProduto.error ?? updateProduto.error;

  useEffect(() => {
    if (isEdit && produtoQuery.data) {
      form.reset({
        nome: produtoQuery.data.nome,
        descricao: produtoQuery.data.descricao ?? "",
        preco: Number(produtoQuery.data.preco),
        estoque: produtoQuery.data.estoque,
        ativo: produtoQuery.data.ativo
      });
    }
  }, [form, isEdit, produtoQuery.data]);

  async function onSubmit(values: ProdutoFormValues) {
    const payload: ProdutoPayload = { ...values };

    if (isEdit && produtoId) {
      await updateProduto.mutateAsync(payload);
    } else {
      await createProduto.mutateAsync(payload);
    }

    router.push("/produtos?salvo=1");
  }

  if (isEdit && produtoQuery.isLoading) {
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

  if (isEdit && produtoQuery.isError) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Produto não carregado</AlertTitle>
        <AlertDescription>{produtoQuery.error.message}</AlertDescription>
      </Alert>
    );
  }

  return (
    <section className="mx-auto w-full max-w-5xl space-y-5">
      <Button asChild variant="ghost" className="px-0">
        <Link href="/produtos">
          <ArrowLeft className="size-4" />
          Voltar para produtos
        </Link>
      </Button>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
          <div className="grid gap-5 lg:grid-cols-[1fr_18rem]">
            <ProdutoPrimaryFields form={form} isEdit={isEdit} preco={preco} />
            <ProdutoOperationalFields form={form} ativo={ativo} />
          </div>
          {mutationError ? (
            <Alert variant="destructive">
              <AlertTitle>Erro ao salvar produto</AlertTitle>
              <AlertDescription>{mutationError.message}</AlertDescription>
            </Alert>
          ) : null}
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button asChild variant="outline" type="button">
              <Link href="/produtos">Cancelar</Link>
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <Loader2 className="size-4 animate-spin" />
              ) : null}
              Salvar produto
            </Button>
          </div>
        </form>
      </Form>
    </section>
  );
}
