"use client";

import { Plus, Trash2 } from "lucide-react";
import { useFieldArray, type UseFormReturn } from "react-hook-form";

import type {
  BarbeiroFormInput,
  BarbeiroFormValues
} from "@/components/barbeiros/barbeiroFormSchema";
import { Button } from "@/components/ui/button";
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
  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "disponibilidades"
  });
  const errors = form.formState.errors.disponibilidades;

  function addDisponibilidade() {
    append({
      dia_semana: "SEGUNDA",
      hora_inicio: "",
      hora_fim: ""
    });
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <CardTitle>Disponibilidade</CardTitle>
            <CardDescription>
              Cadastre um ou mais dias e janelas de horário por barbeiro.
            </CardDescription>
          </div>
          <Button type="button" variant="outline" onClick={addDisponibilidade}>
            <Plus className="size-4" />
            Adicionar horário
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {fields.map((field, index) => (
          <div
            key={field.id}
            className="grid gap-4 rounded-lg border p-4 sm:grid-cols-[1fr_9rem_9rem_auto] sm:items-end">
            <FormField<BarbeiroFormInput>
              name={`disponibilidades.${index}.dia_semana`}>
              {(field) => (
                <FormItem>
                  <FormLabel htmlFor={`disponibilidade-${index}-dia`}>
                    Dia
                  </FormLabel>
                  <FormControl>
                    <select
                      id={`disponibilidade-${index}-dia`}
                      className="h-10 w-full rounded-lg border px-3 text-sm"
                      {...field}>
                      {dias.map(([value, label]) => (
                        <option key={value} value={value}>
                          {label}
                        </option>
                      ))}
                    </select>
                  </FormControl>
                  <FormMessage>
                    {errors?.[index]?.dia_semana?.message}
                  </FormMessage>
                </FormItem>
              )}
            </FormField>
            <FormField<BarbeiroFormInput>
              name={`disponibilidades.${index}.hora_inicio`}>
              {(field) => (
                <FormItem>
                  <FormLabel htmlFor={`disponibilidade-${index}-inicio`}>
                    Início
                  </FormLabel>
                  <FormControl>
                    <Input
                      id={`disponibilidade-${index}-inicio`}
                      type="time"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage>
                    {errors?.[index]?.hora_inicio?.message}
                  </FormMessage>
                </FormItem>
              )}
            </FormField>
            <FormField<BarbeiroFormInput>
              name={`disponibilidades.${index}.hora_fim`}>
              {(field) => (
                <FormItem>
                  <FormLabel htmlFor={`disponibilidade-${index}-fim`}>
                    Fim
                  </FormLabel>
                  <FormControl>
                    <Input
                      id={`disponibilidade-${index}-fim`}
                      type="time"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage>
                    {errors?.[index]?.hora_fim?.message}
                  </FormMessage>
                </FormItem>
              )}
            </FormField>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              aria-label="Remover disponibilidade"
              disabled={fields.length === 1}
              onClick={() => remove(index)}>
              <Trash2 className="size-4" />
            </Button>
          </div>
        ))}
        {typeof errors?.message === "string" ? (
          <p className="text-destructive text-sm">{errors.message}</p>
        ) : null}
      </CardContent>
    </Card>
  );
}
