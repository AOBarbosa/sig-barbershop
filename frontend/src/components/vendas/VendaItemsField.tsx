"use client";

import type { UseFormReturn } from "react-hook-form";

import type {
  VendaFormInput,
  VendaFormValues
} from "@/components/vendas/vendaFormSchema";
import type { Produto } from "@/types/produto";

type VendaFormInstance = UseFormReturn<
  VendaFormInput,
  unknown,
  VendaFormValues
>;

export function VendaItemsField({
  form,
  produtos
}: {
  form: VendaFormInstance;
  produtos: Produto[];
}) {
  return (
    <div className="space-y-3">
      {produtos
        .filter((produto) => produto.ativo)
        .map((produto) => (
          <div
            key={produto.id_produto}
            className="flex items-center justify-between gap-3 rounded-lg border p-3">
            <div className="min-w-0">
              <p className="text-sm font-medium">{produto.nome}</p>
              <p className="text-muted-foreground text-xs">
                {produto.categoria ?? "Sem categoria"}
              </p>
            </div>
            <input
              type="number"
              min="0"
              step="1"
              defaultValue={0}
              aria-label={`Quantidade de ${produto.nome}`}
              className="h-9 w-20 rounded-lg border px-2 text-sm"
              {...form.register(`itens.${produto.id_produto}`)}
            />
          </div>
        ))}
    </div>
  );
}
