"use client";

import type { UseFormReturn } from "react-hook-form";

import type {
  ClienteFormInput,
  ClienteFormValues
} from "@/components/clientes/clienteFormSchema";
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

type ClienteFormInstance = UseFormReturn<
  ClienteFormInput,
  unknown,
  ClienteFormValues
>;

export function ClientePrimaryFields({
  form,
  isEdit
}: {
  form: ClienteFormInstance;
  isEdit: boolean;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{isEdit ? "Editar cliente" : "Novo cliente"}</CardTitle>
        <CardDescription>
          Dados pessoais usados para identificação.
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
      </CardContent>
    </Card>
  );
}

export function ClienteContactFields({ form }: { form: ClienteFormInstance }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Contato</CardTitle>
        <CardDescription>
          Informações opcionais para comunicação.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        <FormField name="email">
          {(field) => (
            <FormItem>
              <FormLabel htmlFor="email">Email</FormLabel>
              <FormControl>
                <Input
                  id="email"
                  type="email"
                  placeholder="cliente@email.com"
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
