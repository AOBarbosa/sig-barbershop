"use client";

import type { UseFormReturn } from "react-hook-form";

import type {
  ServicoFormInput,
  ServicoFormValues
} from "@/components/servicos/servicoFormSchema";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from "@/components/ui/card";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";

const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL"
});

type ServicoFormInstance = UseFormReturn<
  ServicoFormInput,
  unknown,
  ServicoFormValues
>;

export function ServicoPrimaryFields({
  form,
  isEdit,
  preco
}: {
  form: ServicoFormInstance;
  isEdit: boolean;
  preco: number;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{isEdit ? "Editar serviço" : "Novo serviço"}</CardTitle>
        <CardDescription>
          Dados principais exibidos no catálogo.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        <FormField name="nome">
          {(field) => (
            <FormItem>
              <FormLabel htmlFor="nome">Nome</FormLabel>
              <FormControl>
                <Input id="nome" placeholder="Corte masculino" {...field} />
              </FormControl>
              <FormMessage>{form.formState.errors.nome?.message}</FormMessage>
            </FormItem>
          )}
        </FormField>
        <FormField name="descricao">
          {(field) => (
            <FormItem>
              <FormLabel htmlFor="descricao">Descrição</FormLabel>
              <FormControl>
                <Textarea
                  id="descricao"
                  placeholder="Detalhes do serviço"
                  {...field}
                />
              </FormControl>
            </FormItem>
          )}
        </FormField>
        <FormField name="preco">
          {(field) => (
            <FormItem>
              <FormLabel htmlFor="preco">Preço</FormLabel>
              <FormControl>
                <Input
                  id="preco"
                  type="number"
                  min="0"
                  step="0.01"
                  {...field}
                />
              </FormControl>
              <FormMessage>{form.formState.errors.preco?.message}</FormMessage>
              <p className="text-muted-foreground text-sm">
                Preço formatado: {currencyFormatter.format(preco)}
              </p>
            </FormItem>
          )}
        </FormField>
      </CardContent>
    </Card>
  );
}

export function ServicoOperationalFields({
  form,
  ativo
}: {
  form: ServicoFormInstance;
  ativo: boolean;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Configuração operacional</CardTitle>
        <CardDescription>
          Controle de disponibilidade e duração.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        <FormField name="duracao_minutos">
          {(field) => (
            <FormItem>
              <FormLabel htmlFor="duracao_minutos">
                Duração em minutos
              </FormLabel>
              <FormControl>
                <Input
                  id="duracao_minutos"
                  type="number"
                  min="1"
                  step="1"
                  {...field}
                />
              </FormControl>
              <FormMessage>
                {form.formState.errors.duracao_minutos?.message}
              </FormMessage>
            </FormItem>
          )}
        </FormField>
        <FormItem>
          <div className="flex items-center justify-between rounded-lg border p-3">
            <div className="space-y-1">
              <FormLabel htmlFor="ativo">Serviço ativo</FormLabel>
              <p className="text-muted-foreground text-sm">
                {ativo
                  ? "Disponível para novos atendimentos"
                  : "Oculto em novos fluxos operacionais"}
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
  );
}
