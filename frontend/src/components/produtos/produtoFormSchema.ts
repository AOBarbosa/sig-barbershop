import { z } from "zod";

export const produtoFormSchema = z.object({
  nome: z.string().trim().min(1, "Nome é obrigatório"),
  categoria: z
    .string()
    .trim()
    .or(z.literal(""))
    .transform((value) => (value === "" ? null : value)),
  preco_venda: z.coerce.number().min(0, "Preço de venda deve ser positivo"),
  preco_custo: z.coerce.number().min(0, "Preço de custo deve ser positivo"),
  pontos_gerados: z.coerce.number().int().min(0, "Pontos deve ser positivo"),
  ativo: z.boolean()
});

export type ProdutoFormInput = z.input<typeof produtoFormSchema>;
export type ProdutoFormValues = z.output<typeof produtoFormSchema>;

export const defaultProdutoFormValues: ProdutoFormInput = {
  nome: "",
  categoria: "",
  preco_venda: 0,
  preco_custo: 0,
  pontos_gerados: 0,
  ativo: true
};
