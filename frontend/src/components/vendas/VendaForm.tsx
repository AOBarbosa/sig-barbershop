"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft, Loader2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";

import {
  defaultVendaFormValues,
  vendaFormSchema,
  type VendaFormInput,
  type VendaFormValues
} from "@/components/vendas/vendaFormSchema";
import { VendaFieldError } from "@/components/vendas/VendaFieldError";
import { VendaItemsField } from "@/components/vendas/VendaItemsField";
import { pessoaNome } from "@/components/vendas/vendaFormatters";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCreateVenda, useVendaLookups } from "@/hooks/useVendas";
import type { FormaPagamento, VendaItemPayload } from "@/types/venda";

const formasPagamento: Array<{ value: FormaPagamento; label: string }> = [
  { value: "dinheiro", label: "Dinheiro" },
  { value: "cartao_debito", label: "Cartão de débito" },
  { value: "cartao_credito", label: "Cartão de crédito" },
  { value: "pix", label: "Pix" }
];

export function VendaForm() {
  const router = useRouter();
  const lookupsQuery = useVendaLookups();
  const createVenda = useCreateVenda();
  const form = useForm<VendaFormInput, unknown, VendaFormValues>({
    resolver: zodResolver(vendaFormSchema),
    defaultValues: defaultVendaFormValues
  });

  async function onSubmit(values: VendaFormValues) {
    const itens: VendaItemPayload[] = Object.entries(values.itens)
      .filter(([, quantidade]) => quantidade > 0)
      .map(([produtoId, quantidade]) => ({
        PRODUTO_id_produto: Number(produtoId),
        quantidade
      }));

    await createVenda.mutateAsync({
      CLIENTE_id_cliente: values.CLIENTE_id_cliente,
      CAIXA_id_caixa: values.CAIXA_id_caixa,
      forma_pagamento: (values.forma_pagamento ||
        null) as FormaPagamento | null,
      itens
    });
    router.push("/vendas?salvo=1");
  }

  if (lookupsQuery.isLoading) {
    return <Skeleton className="mx-auto h-96 w-full max-w-5xl" />;
  }

  if (lookupsQuery.isError) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Dados de apoio não carregados</AlertTitle>
        <AlertDescription>{lookupsQuery.error.message}</AlertDescription>
      </Alert>
    );
  }

  const lookups = lookupsQuery.data;

  if (!lookups) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Dados não encontrados</AlertTitle>
        <AlertDescription>
          Não foi possível montar o formulário de venda.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <section className="mx-auto w-full max-w-5xl space-y-5">
      <Button asChild variant="ghost" className="px-0">
        <Link href="/vendas">
          <ArrowLeft className="size-4" />
          Voltar para vendas
        </Link>
      </Button>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
        <Card>
          <CardHeader>
            <CardTitle>Nova venda</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2">
            <VendaFieldError
              message={form.formState.errors.CLIENTE_id_cliente?.message}>
              <label className="text-sm font-medium" htmlFor="cliente">
                Cliente
              </label>
              <select
                id="cliente"
                className="h-10 rounded-lg border px-3 text-sm"
                {...form.register("CLIENTE_id_cliente")}
                name="CLIENTE_id_cliente">
                <option value={0}>Selecione</option>
                {lookups.clientes.map((cliente) => (
                  <option key={cliente.id_cliente} value={cliente.id_cliente}>
                    {pessoaNome(cliente.PESSOA_id_pessoa, lookups)}
                  </option>
                ))}
              </select>
            </VendaFieldError>
            <VendaFieldError
              message={form.formState.errors.CAIXA_id_caixa?.message}>
              <label className="text-sm font-medium" htmlFor="caixa">
                Caixa
              </label>
              <select
                id="caixa"
                className="h-10 rounded-lg border px-3 text-sm"
                {...form.register("CAIXA_id_caixa")}
                name="CAIXA_id_caixa">
                <option value={0}>Selecione</option>
                {lookups.caixas.map((caixa) => (
                  <option key={caixa.id_caixa} value={caixa.id_caixa}>
                    {pessoaNome(caixa.PESSOA_id_pessoa, lookups)}
                  </option>
                ))}
              </select>
            </VendaFieldError>
            <div className="space-y-2 md:col-span-2">
              <label className="text-sm font-medium" htmlFor="forma_pagamento">
                Forma de pagamento
              </label>
              <select
                id="forma_pagamento"
                className="h-10 rounded-lg border px-3 text-sm"
                {...form.register("forma_pagamento")}
                name="forma_pagamento">
                <option value="">Não informar</option>
                {formasPagamento.map((forma) => (
                  <option key={forma.value} value={forma.value}>
                    {forma.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-3 md:col-span-2">
              <p className="text-sm font-medium">Produtos</p>
              <VendaItemsField form={form} produtos={lookups.produtos} />
              <p className="text-destructive text-sm">
                {
                  (
                    form.formState.errors.itens as
                      { message?: string } | undefined
                  )?.message
                }
              </p>
            </div>
          </CardContent>
        </Card>
        {createVenda.error ? (
          <Alert variant="destructive">
            <AlertTitle>Erro ao salvar venda</AlertTitle>
            <AlertDescription>{createVenda.error.message}</AlertDescription>
          </Alert>
        ) : null}
        <div className="flex justify-end">
          <Button type="submit" disabled={createVenda.isPending}>
            {createVenda.isPending ? (
              <Loader2 className="size-4 animate-spin" />
            ) : null}
            Salvar venda
          </Button>
        </div>
      </form>
    </section>
  );
}
