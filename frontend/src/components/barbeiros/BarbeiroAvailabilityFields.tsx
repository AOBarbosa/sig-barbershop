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

const dias = [
  ["SEGUNDA", "Segunda"],
  ["TERCA", "Terça"],
  ["QUARTA", "Quarta"],
  ["QUINTA", "Quinta"],
  ["SEXTA", "Sexta"],
  ["SABADO", "Sábado"],
  ["DOMINGO", "Domingo"]
];

export function BarbeiroAvailabilityFields({
  form
}: {
  form: BarbeiroFormInstance;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Disponibilidade</CardTitle>
        <CardDescription>
          Primeiro horário de agenda do barbeiro.
        </CardDescription>
      </CardHeader>
      <CardContent className="grid gap-4 sm:grid-cols-3">
        <FormField name="dia_semana">
          {(field) => (
            <FormItem>
              <FormLabel htmlFor="dia_semana">Dia</FormLabel>
              <FormControl>
                <select
                  id="dia_semana"
                  className="h-10 rounded-lg border px-3 text-sm"
                  {...field}>
                  {dias.map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </FormControl>
              <FormMessage>
                {form.formState.errors.dia_semana?.message}
              </FormMessage>
            </FormItem>
          )}
        </FormField>
        <FormField name="hora_inicio">
          {(field) => (
            <FormItem>
              <FormLabel htmlFor="hora_inicio">Início</FormLabel>
              <FormControl>
                <Input id="hora_inicio" type="time" {...field} />
              </FormControl>
              <FormMessage>
                {form.formState.errors.hora_inicio?.message}
              </FormMessage>
            </FormItem>
          )}
        </FormField>
        <FormField name="hora_fim">
          {(field) => (
            <FormItem>
              <FormLabel htmlFor="hora_fim">Fim</FormLabel>
              <FormControl>
                <Input id="hora_fim" type="time" {...field} />
              </FormControl>
              <FormMessage>
                {form.formState.errors.hora_fim?.message}
              </FormMessage>
            </FormItem>
          )}
        </FormField>
      </CardContent>
    </Card>
  );
}
