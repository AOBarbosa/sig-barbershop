"use client";

import type { UseFormReturn } from "react-hook-form";

import type {
  FidelidadeFormInput,
  FidelidadeFormValues
} from "@/components/fidelidade/fidelidadeFormSchema";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Switch } from "@/components/ui/switch";
import type { Produto } from "@/types/produto";
import type { Servico } from "@/types/servico";

type FidelidadeFormApi = UseFormReturn<
  FidelidadeFormInput,
  unknown,
  FidelidadeFormValues
>;

export function FidelidadeRuleFields({
  form,
  lookups,
  tipo,
  ativo
}: {
  form: FidelidadeFormApi;
  lookups: { servicos: Servico[]; produtos: Produto[] };
  tipo: "servico" | "produto";
  ativo: boolean;
}) {
  return (
    <>
      <FormItem>
        <FormLabel>Aplicar regra a</FormLabel>
        <RadioGroup
          value={tipo}
          onValueChange={(value) =>
            form.setValue("tipo", value as "servico" | "produto", {
              shouldDirty: true,
              shouldValidate: true
            })
          }
          className="grid grid-cols-2 gap-3">
          <label className="flex cursor-pointer items-center gap-2 rounded-lg border p-3 text-sm">
            <RadioGroupItem value="servico" />
            Serviço
          </label>
          <label className="flex cursor-pointer items-center gap-2 rounded-lg border p-3 text-sm">
            <RadioGroupItem value="produto" />
            Produto
          </label>
        </RadioGroup>
        <FormMessage>{form.formState.errors.tipo?.message}</FormMessage>
      </FormItem>
      {tipo === "servico" ? (
        <FormField name="SERVICO_id_servico">
          {(field) => (
            <FormItem>
              <FormLabel htmlFor="servico">Serviço</FormLabel>
              <FormControl>
                <select
                  id="servico"
                  className="h-10 w-full rounded-lg border px-3 text-sm"
                  {...field}>
                  <option value="">Selecione</option>
                  {lookups.servicos
                    .filter((servico) => servico.ativo)
                    .map((servico) => (
                      <option
                        key={servico.id_servico}
                        value={servico.id_servico}>
                        {servico.nome}
                      </option>
                    ))}
                </select>
              </FormControl>
            </FormItem>
          )}
        </FormField>
      ) : (
        <FormField name="PRODUTO_id_produto">
          {(field) => (
            <FormItem>
              <FormLabel htmlFor="produto">Produto</FormLabel>
              <FormControl>
                <select
                  id="produto"
                  className="h-10 w-full rounded-lg border px-3 text-sm"
                  {...field}>
                  <option value="">Selecione</option>
                  {lookups.produtos
                    .filter((produto) => produto.ativo)
                    .map((produto) => (
                      <option
                        key={produto.id_produto}
                        value={produto.id_produto}>
                        {produto.nome}
                      </option>
                    ))}
                </select>
              </FormControl>
            </FormItem>
          )}
        </FormField>
      )}
      <FormField name="pontos">
        {(field) => (
          <FormItem>
            <FormLabel htmlFor="pontos">Pontos</FormLabel>
            <FormControl>
              <Input id="pontos" type="number" min="1" step="1" {...field} />
            </FormControl>
            <FormMessage>{form.formState.errors.pontos?.message}</FormMessage>
          </FormItem>
        )}
      </FormField>
      <FormItem>
        <div className="flex items-center justify-between rounded-lg border p-3">
          <div className="space-y-1">
            <FormLabel htmlFor="ativo">Regra ativa</FormLabel>
            <p className="text-muted-foreground text-sm">
              {ativo
                ? "Pontos são concedidos nas próximas vendas/atendimentos"
                : "Regra desativada, não concede mais pontos"}
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
    </>
  );
}
