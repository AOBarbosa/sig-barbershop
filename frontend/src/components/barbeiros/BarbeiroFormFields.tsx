"use client";

import type { UseFormReturn } from "react-hook-form";

import type {
  BarbeiroFormInput,
  BarbeiroFormValues
} from "@/components/barbeiros/barbeiroFormSchema";
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

type BarbeiroFormInstance = UseFormReturn<
  BarbeiroFormInput,
  unknown,
  BarbeiroFormValues
>;

export function BarbeiroPrimaryFields({
  form,
  isEdit
}: {
  form: BarbeiroFormInstance;
  isEdit: boolean;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{isEdit ? "Editar barbeiro" : "Novo barbeiro"}</CardTitle>
        <CardDescription>
          Dados pessoais e informações profissionais.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        <FormField name="nome">
          {(field) => (
            <FormItem>
              <FormLabel htmlFor="nome">Nome</FormLabel>
              <FormControl>
                <Input id="nome" placeholder="Nome completo" {...field} />
              </FormControl>
              <FormMessage>{form.formState.errors.nome?.message}</FormMessage>
            </FormItem>
          )}
        </FormField>
        <FormField name="cpf">
          {(field) => (
            <FormItem>
              <FormLabel htmlFor="cpf">CPF</FormLabel>
              <FormControl>
                <Input
                  id="cpf"
                  placeholder="Somente números"
                  inputMode="numeric"
                  maxLength={11}
                  {...field}
                />
              </FormControl>
              <FormMessage>{form.formState.errors.cpf?.message}</FormMessage>
            </FormItem>
          )}
        </FormField>
        <FormField name="email">
          {(field) => (
            <FormItem>
              <FormLabel htmlFor="email">Email</FormLabel>
              <FormControl>
                <Input
                  id="email"
                  type="email"
                  placeholder="barbeiro@email.com"
                  {...field}
                />
              </FormControl>
              <FormMessage>{form.formState.errors.email?.message}</FormMessage>
            </FormItem>
          )}
        </FormField>
        <FormField name="data_nascimento">
          {(field) => (
            <FormItem>
              <FormLabel htmlFor="data_nascimento">
                Data de nascimento
              </FormLabel>
              <FormControl>
                <Input id="data_nascimento" type="date" {...field} />
              </FormControl>
              <FormMessage>
                {form.formState.errors.data_nascimento?.message}
              </FormMessage>
            </FormItem>
          )}
        </FormField>
      </CardContent>
    </Card>
  );
}

export function BarbeiroProfessionalFields({
  form,
  ativo
}: {
  form: BarbeiroFormInstance;
  ativo: boolean;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Perfil profissional</CardTitle>
        <CardDescription>
          Configurações da atuação do barbeiro.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        <FormField name="especialidade">
          {(field) => (
            <FormItem>
              <FormLabel htmlFor="especialidade">Especialidade</FormLabel>
              <FormControl>
                <Input
                  id="especialidade"
                  placeholder="Corte, barba, coloração..."
                  {...field}
                />
              </FormControl>
              <FormMessage>
                {form.formState.errors.especialidade?.message}
              </FormMessage>
            </FormItem>
          )}
        </FormField>
        <FormItem>
          <div className="flex items-center justify-between rounded-lg border p-3">
            <div className="space-y-1">
              <FormLabel htmlFor="ativo">Barbeiro ativo</FormLabel>
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
