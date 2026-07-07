import { z } from "zod";

export const vendaFormSchema = z
  .object({
    CLIENTE_id_cliente: z.coerce.number().positive("Cliente é obrigatório"),
    CAIXA_id_caixa: z.coerce.number().positive("Caixa é obrigatório"),
    forma_pagamento: z.string(),
    itens: z.record(z.string(), z.coerce.number().int().nonnegative())
  })
  .refine(
    (data) => Object.values(data.itens).some((quantidade) => quantidade > 0),
    { message: "Selecione ao menos um produto", path: ["itens"] }
  );

export type VendaFormInput = z.input<typeof vendaFormSchema>;
export type VendaFormValues = z.output<typeof vendaFormSchema>;

export const defaultVendaFormValues: VendaFormValues = {
  CLIENTE_id_cliente: 0,
  CAIXA_id_caixa: 0,
  forma_pagamento: "",
  itens: {}
};
