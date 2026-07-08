"use client";

import type { UseFormReturn } from "react-hook-form";

import type {
  ProdutoFormInput,
  ProdutoFormValues
} from "@/components/produtos/produtoFormSchema";
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

type ProdutoFormInstance = UseFormReturn<
  ProdutoFormInput,
  unknown,
  ProdutoFormValues
>;

export function ProdutoPrimaryFields({
  form,
  isEdit,
  mostrarPrecoCusto
}: {
  form: ProdutoFormInstance;
  isEdit: boolean;
  mostrarPrecoCusto: boolean;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{isEdit ? "Editar produto" : "Novo produto"}</CardTitle>
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
                <Input id="nome" placeholder="Pomada modeladora" {...field} />
              </FormControl>
              <FormMessage>{form.formState.errors.nome?.message}</FormMessage>
            </FormItem>
          )}
        </FormField>
        <FormField name="categoria">
          {(field) => (
            <FormItem>
              <FormLabel htmlFor="categoria">Categoria</FormLabel>
              <FormControl>
                <Input id="categoria" placeholder="Finalizador" {...field} />
              </FormControl>
              <FormMessage>
                {form.formState.errors.categoria?.message}
              </FormMessage>
            </FormItem>
          )}
        </FormField>
        <div className="grid gap-4 sm:grid-cols-3">
          <FormField name="preco_venda">
            {(field) => (
              <FormItem>
                <FormLabel htmlFor="preco_venda">Preço venda</FormLabel>
                <FormControl>
                  <Input
                    id="preco_venda"
                    type="number"
                    step="0.01"
                    {...field}
                  />
                </FormControl>
                <FormMessage>
                  {form.formState.errors.preco_venda?.message}
                </FormMessage>
              </FormItem>
            )}
          </FormField>
          {mostrarPrecoCusto ? (
            <FormField name="preco_custo">
              {(field) => (
                <FormItem>
                  <FormLabel htmlFor="preco_custo">Preço custo</FormLabel>
                  <FormControl>
                    <Input
                      id="preco_custo"
                      type="number"
                      step="0.01"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage>
                    {form.formState.errors.preco_custo?.message}
                  </FormMessage>
                </FormItem>
              )}
            </FormField>
          ) : (
            <FormItem>
              <FormLabel htmlFor="preco_custo">Preço custo</FormLabel>
              <FormControl>
                <Input
                  id="preco_custo"
                  name="preco_custo"
                  disabled
                  value="Visível apenas para administradores"
                  readOnly
                />
              </FormControl>
            </FormItem>
          )}
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

export function ProdutoOperationalFields({
  form,
  ativo
}: {
  form: ProdutoFormInstance;
  ativo: boolean;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Configuração operacional</CardTitle>
        <CardDescription>
          Disponibilidade do produto no catálogo.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        <FormItem>
          <div className="flex items-center justify-between rounded-lg border p-3">
            <div className="space-y-1">
              <FormLabel htmlFor="ativo">Produto ativo</FormLabel>
              <p className="text-muted-foreground text-sm">
                {ativo
                  ? "Disponível para novas vendas"
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
