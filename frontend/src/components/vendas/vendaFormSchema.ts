import { z } from "zod";

export const vendaFormSchema = z
  .object({
    CLIENTE_PESSOA_id_pessoa: z.coerce
      .number()
      .positive("Cliente é obrigatório"),
    CAIXA_PESSOA_id_pessoa: z.coerce.number().positive("Caixa é obrigatório"),
    data_hora: z.string().min(1, "Data e hora são obrigatórias"),
    forma_pagamento: z.string().min(1, "Forma de pagamento é obrigatória"),
    itens: z.record(z.string(), z.coerce.number().int().nonnegative())
  })
  .refine(
    (data) => Object.values(data.itens).some((quantidade) => quantidade > 0),
    { message: "Selecione ao menos um produto", path: ["itens"] }
  );

export type VendaFormInput = z.input<typeof vendaFormSchema>;
export type VendaFormValues = z.output<typeof vendaFormSchema>;

export const defaultVendaFormValues: VendaFormValues = {
  CLIENTE_PESSOA_id_pessoa: 0,
  CAIXA_PESSOA_id_pessoa: 0,
  data_hora: "",
  forma_pagamento: "PIX",
  itens: {}
};
