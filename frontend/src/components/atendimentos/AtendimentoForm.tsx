"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm, useWatch } from "react-hook-form";

import { AtendimentoAvailabilityHint } from "@/components/atendimentos/AtendimentoAvailabilityHint";
import { AtendimentoErrorAlert } from "@/components/atendimentos/AtendimentoErrorAlert";
import { AtendimentoFieldError } from "@/components/atendimentos/AtendimentoFieldError";
import { AtendimentoMissingDataAlert } from "@/components/atendimentos/AtendimentoMissingDataAlert";
import { AtendimentoSubmitButton } from "@/components/atendimentos/AtendimentoSubmitButton";
import { AtendimentoTimeField } from "@/components/atendimentos/AtendimentoTimeField";
import {
  defaultAtendimentoFormValues,
  atendimentoFormSchema,
  type AtendimentoFormInput,
  type AtendimentoFormValues
} from "@/components/atendimentos/atendimentoFormSchema";
import { gerarHorariosDisponiveis } from "@/components/atendimentos/atendimentoSlots";
import { pessoaNome } from "@/components/atendimentos/atendimentoFormatters";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Form } from "@/components/ui/form";
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
    useWatch({ control: form.control, name: "BARBEIRO_PESSOA_id_pessoa" })
  );
  const disponibilidadesQuery = useDisponibilidadesDoBarbeiro(barbeiroId);

  async function onSubmit(values: AtendimentoFormValues) {
    const dataHora =
      values.data_hora_inicio.length === 16
        ? `${values.data_hora_inicio}:00`
        : values.data_hora_inicio;

    await createAtendimento.mutateAsync({
      CLIENTE_PESSOA_id_pessoa: values.CLIENTE_PESSOA_id_pessoa,
      BARBEIRO_PESSOA_id_pessoa: values.BARBEIRO_PESSOA_id_pessoa,
      data_hora_inicio: dataHora,
      data_hora_fim: null,
      status: "AGENDADO",
      observacoes: values.observacoes || null,
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

  const horariosDisponiveis = gerarHorariosDisponiveis({
    barbeiroId,
    disponibilidades: disponibilidadesQuery.data ?? [],
    atendimentos: lookups.atendimentos
  });

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
                message={
                  form.formState.errors.CLIENTE_PESSOA_id_pessoa?.message
                }>
                <label className="text-sm font-medium" htmlFor="cliente">
                  Cliente
                </label>
                <select
                  id="cliente"
                  className="h-10 rounded-lg border px-3 text-sm"
                  {...form.register("CLIENTE_PESSOA_id_pessoa")}
                  name="CLIENTE_PESSOA_id_pessoa">
                  <option value={0}>Selecione</option>
                  {lookups.clientes.map((cliente) => (
                    <option
                      key={cliente.PESSOA_id_pessoa}
                      value={cliente.PESSOA_id_pessoa}>
                      {pessoaNome(cliente.PESSOA_id_pessoa, lookups)}
                    </option>
                  ))}
                </select>
              </AtendimentoFieldError>
              <AtendimentoFieldError
                message={
                  form.formState.errors.BARBEIRO_PESSOA_id_pessoa?.message
                }>
                <label className="text-sm font-medium" htmlFor="barbeiro">
                  Barbeiro
                </label>
                <select
                  id="barbeiro"
                  className="h-10 rounded-lg border px-3 text-sm"
                  {...form.register("BARBEIRO_PESSOA_id_pessoa")}
                  name="BARBEIRO_PESSOA_id_pessoa">
                  <option value={0}>Selecione</option>
                  {lookups.barbeiros.map((barbeiro) => (
                    <option
                      key={barbeiro.PESSOA_id_pessoa}
                      value={barbeiro.PESSOA_id_pessoa}>
                      {pessoaNome(barbeiro.PESSOA_id_pessoa, lookups)}
                    </option>
                  ))}
                </select>
              </AtendimentoFieldError>
              <AtendimentoTimeField
                error={form.formState.errors.data_hora_inicio?.message}
                loading={disponibilidadesQuery.isLoading}
                barbeiroId={barbeiroId}
                horarios={horariosDisponiveis}
                register={form.register("data_hora_inicio")}
              />
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
                <label className="text-sm font-medium" htmlFor="observacoes">
                  Observação
                </label>
                <Textarea id="observacoes" {...form.register("observacoes")} />
              </div>
            </CardContent>
          </Card>
          <AtendimentoErrorAlert message={createAtendimento.error?.message} />
          <div className="flex justify-end">
            <AtendimentoSubmitButton loading={createAtendimento.isPending} />
          </div>
        </form>
      </Form>
    </section>
  );
}
