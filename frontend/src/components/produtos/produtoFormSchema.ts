import { z } from "zod";

export const produtoFormSchema = z.object({
  nome: z.string().trim().min(1, "Nome é obrigatório"),
  descricao: z.string(),
  preco: z.coerce.number().positive("Preço deve ser maior que zero"),
  estoque: z.coerce
    .number()
    .int("Estoque deve ser um número inteiro")
    .nonnegative("Estoque não pode ser negativo"),
  ativo: z.boolean()
});

export type ProdutoFormInput = z.input<typeof produtoFormSchema>;
export type ProdutoFormValues = z.output<typeof produtoFormSchema>;

export const defaultProdutoFormValues: ProdutoFormInput = {
  nome: "",
  descricao: "",
  preco: 0,
  estoque: 0,
  ativo: true
};
