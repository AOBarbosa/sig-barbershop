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
  form
}: {
  form: BarbeiroFormInstance;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Perfil profissional</CardTitle>
        <CardDescription>Configurações da atuação do barbeiro.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        <FormField name="apelido">
          {(field) => (
            <FormItem>
              <FormLabel htmlFor="apelido">Apelido</FormLabel>
              <FormControl>
                <Input
                  id="apelido"
                  placeholder="Nome usado na equipe"
                  {...field}
                />
              </FormControl>
              <FormMessage>
                {form.formState.errors.apelido?.message}
              </FormMessage>
            </FormItem>
          )}
        </FormField>
        <FormField name="comissao_percentual">
          {(field) => (
            <FormItem>
              <FormLabel htmlFor="comissao_percentual">Comissão (%)</FormLabel>
              <FormControl>
                <Input
                  id="comissao_percentual"
                  type="number"
                  min="0"
                  max="100"
                  step="0.01"
                  {...field}
                />
              </FormControl>
              <FormMessage>
                {form.formState.errors.comissao_percentual?.message}
              </FormMessage>
            </FormItem>
          )}
        </FormField>
      </CardContent>
    </Card>
  );
}
