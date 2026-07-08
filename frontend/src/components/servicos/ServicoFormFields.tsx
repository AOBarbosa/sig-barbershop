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

type ServicoFormInstance = UseFormReturn<
  ServicoFormInput,
  unknown,
  ServicoFormValues
>;

export function ServicoPrimaryFields({
  form,
  isEdit
}: {
  form: ServicoFormInstance;
  isEdit: boolean;
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
        <div className="grid gap-4 sm:grid-cols-3">
          <FormField name="preco">
            {(field) => (
              <FormItem>
                <FormLabel htmlFor="preco">Preço</FormLabel>
                <FormControl>
                  <Input id="preco" type="number" step="0.01" {...field} />
                </FormControl>
                <FormMessage>
                  {form.formState.errors.preco?.message}
                </FormMessage>
              </FormItem>
            )}
          </FormField>
          <FormField name="duracao_em_minutos">
            {(field) => (
              <FormItem>
                <FormLabel htmlFor="duracao_em_minutos">Duração</FormLabel>
                <FormControl>
                  <Input
                    id="duracao_em_minutos"
                    type="number"
                    step="1"
                    {...field}
                  />
                </FormControl>
                <FormMessage>
                  {form.formState.errors.duracao_em_minutos?.message}
                </FormMessage>
              </FormItem>
            )}
          </FormField>
          <FormField name="pontos_gerados">
            {(field) => (
              <FormItem>
                <FormLabel htmlFor="pontos_gerados">Pontos</FormLabel>
                <FormControl>
                  <Input
                    id="pontos_gerados"
                    type="number"
                    step="1"
                    {...field}
                  />
                </FormControl>
                <FormMessage>
                  {form.formState.errors.pontos_gerados?.message}
                </FormMessage>
              </FormItem>
            )}
          </FormField>
        </div>
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
          Disponibilidade do serviço no catálogo.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
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
