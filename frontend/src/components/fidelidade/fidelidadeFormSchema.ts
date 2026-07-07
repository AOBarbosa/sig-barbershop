import { z } from "zod";

const baseFidelidadeFormSchema = z.object({
  tipo: z.enum(["servico", "produto"]),
  SERVICO_id_servico: z.coerce.number().optional(),
  PRODUTO_id_produto: z.coerce.number().optional(),
  pontos: z.coerce.number().int().positive("Pontos deve ser maior que zero"),
  ativo: z.boolean()
});

export const fidelidadeFormSchema = baseFidelidadeFormSchema.superRefine(
  (data, ctx) => {
    const temServico = Boolean(data.SERVICO_id_servico);
    const temProduto = Boolean(data.PRODUTO_id_produto);

    if (temServico && temProduto) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Selecione apenas um: serviço ou produto, nunca os dois",
        path: ["tipo"]
      });
    } else if (!temServico && !temProduto) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Selecione um serviço ou um produto",
        path: ["tipo"]
      });
    }
  }
);

export type FidelidadeFormInput = z.input<typeof fidelidadeFormSchema>;
export type FidelidadeFormValues = z.output<typeof fidelidadeFormSchema>;

export const defaultFidelidadeFormValues: FidelidadeFormInput = {
  tipo: "servico",
  SERVICO_id_servico: undefined,
  PRODUTO_id_produto: undefined,
  pontos: 0,
  ativo: true
};
