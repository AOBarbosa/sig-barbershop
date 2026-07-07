"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useWatch } from "react-hook-form";
import { useForm } from "react-hook-form";

import { AtendimentoAvailabilityHint } from "@/components/atendimentos/AtendimentoAvailabilityHint";
import { AtendimentoFieldError } from "@/components/atendimentos/AtendimentoFieldError";
import { AtendimentoMissingDataAlert } from "@/components/atendimentos/AtendimentoMissingDataAlert";
import { AtendimentoSubmitButton } from "@/components/atendimentos/AtendimentoSubmitButton";
import {
  defaultAtendimentoFormValues,
  atendimentoFormSchema,
  type AtendimentoFormInput,
  type AtendimentoFormValues
} from "@/components/atendimentos/atendimentoFormSchema";
import { pessoaNome } from "@/components/atendimentos/atendimentoFormatters";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Form } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import {
  useAtendimentoLookups,
  useCreateAtendimento,
  useDisponibilidadesDoBarbeiro
} from "@/hooks/useAtendimentos";

export function AtendimentoForm() {
  const router = useRouter();
  const lookupsQuery = useAtendimentoLookups();
  const createAtendimento = useCreateAtendimento();
  const form = useForm<AtendimentoFormInput, unknown, AtendimentoFormValues>({
    resolver: zodResolver(atendimentoFormSchema),
    defaultValues: defaultAtendimentoFormValues
  });
  const barbeiroId = Number(
    useWatch({ control: form.control, name: "BARBEIRO_id_barbeiro" })
  );
  const disponibilidadesQuery = useDisponibilidadesDoBarbeiro(barbeiroId);

  async function onSubmit(values: AtendimentoFormValues) {
    const dataHora =
      values.data_hora.length === 16
        ? `${values.data_hora}:00`
        : values.data_hora;

    await createAtendimento.mutateAsync({
      CLIENTE_id_cliente: values.CLIENTE_id_cliente,
      BARBEIRO_id_barbeiro: values.BARBEIRO_id_barbeiro,
      data_hora: dataHora,
      status: "agendado",
      observacao: values.observacao || null,
      servicoIds: values.servicoIds
    });
    router.push("/atendimentos?salvo=1");
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
      <AtendimentoMissingDataAlert message="Não foi possível montar o formulário de atendimento." />
    );
  }

  return (
    <section className="mx-auto w-full max-w-5xl space-y-5">
      <Button asChild variant="ghost" className="px-0">
        <Link href="/atendimentos">
          <ArrowLeft className="size-4" />
          Voltar para atendimentos
        </Link>
      </Button>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
          <Card>
            <CardHeader>
              <CardTitle>Novo atendimento</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2">
              <AtendimentoFieldError
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
              </AtendimentoFieldError>
              <AtendimentoFieldError
                message={form.formState.errors.BARBEIRO_id_barbeiro?.message}>
                <label className="text-sm font-medium" htmlFor="barbeiro">
                  Barbeiro
                </label>
                <select
                  id="barbeiro"
                  className="h-10 rounded-lg border px-3 text-sm"
                  {...form.register("BARBEIRO_id_barbeiro")}
                  name="BARBEIRO_id_barbeiro">
                  <option value={0}>Selecione</option>
                  {lookups.barbeiros
                    .filter((barbeiro) => barbeiro.ativo)
                    .map((barbeiro) => (
                      <option
                        key={barbeiro.id_barbeiro}
                        value={barbeiro.id_barbeiro}>
                        {pessoaNome(barbeiro.PESSOA_id_pessoa, lookups)}
                      </option>
                    ))}
                </select>
              </AtendimentoFieldError>
              <AtendimentoFieldError
                message={form.formState.errors.data_hora?.message}>
                <label className="text-sm font-medium" htmlFor="data_hora">
                  Data e hora
                </label>
                <Input
                  id="data_hora"
                  type="datetime-local"
                  {...form.register("data_hora")}
                />
              </AtendimentoFieldError>
              <AtendimentoAvailabilityHint
                disponibilidades={disponibilidadesQuery.data}
              />
              <div className="space-y-3 md:col-span-2">
                <p className="text-sm font-medium">Serviços</p>
                <div className="grid gap-2 sm:grid-cols-2">
                  {lookups.servicos
                    .filter((servico) => servico.ativo)
                    .map((servico) => (
                      <label
                        key={servico.id_servico}
                        className="flex cursor-pointer items-center gap-2 rounded-lg border p-3 text-sm">
                        <input
                          type="checkbox"
                          value={servico.id_servico}
                          {...form.register("servicoIds")}
                        />
                        {servico.nome}
                      </label>
                    ))}
                </div>
                <p className="text-destructive text-sm">
                  {form.formState.errors.servicoIds?.message}
                </p>
              </div>
              <div className="space-y-2 md:col-span-2">
                <label className="text-sm font-medium" htmlFor="observacao">
                  Observação
                </label>
                <Textarea id="observacao" {...form.register("observacao")} />
              </div>
            </CardContent>
          </Card>
          {createAtendimento.error ? (
            <Alert variant="destructive">
              <AlertTitle>Erro ao salvar atendimento</AlertTitle>
              <AlertDescription>
                {createAtendimento.error.message}
              </AlertDescription>
            </Alert>
          ) : null}
          <div className="flex justify-end">
            <AtendimentoSubmitButton loading={createAtendimento.isPending} />
          </div>
        </form>
      </Form>
    </section>
  );
}
