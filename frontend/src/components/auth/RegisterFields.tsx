"use client";

import type { UseFormReturn } from "react-hook-form";

import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";

interface RegisterFormValues {
  nome?: string;
  cpf?: string;
  email: string;
  senha: string;
}

export function RegisterFields({
  form
}: {
  form: UseFormReturn<RegisterFormValues>;
}) {
  return (
    <>
      <FormField name="nome">
        {(field) => (
          <FormItem>
            <FormLabel>Nome</FormLabel>
            <FormControl>
              <Input
                {...field}
                autoComplete="name"
                placeholder="Nome completo"
              />
            </FormControl>
            <FormMessage>{form.formState.errors.nome?.message}</FormMessage>
          </FormItem>
        )}
      </FormField>
      <FormField name="cpf">
        {(field) => (
          <FormItem>
            <FormLabel>CPF</FormLabel>
            <FormControl>
              <Input
                {...field}
                inputMode="numeric"
                maxLength={11}
                placeholder="Somente números"
              />
            </FormControl>
            <FormMessage>{form.formState.errors.cpf?.message}</FormMessage>
          </FormItem>
        )}
      </FormField>
    </>
  );
}
