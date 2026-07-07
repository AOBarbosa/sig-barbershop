import { z } from "zod";

export const atendimentoFormSchema = z.object({
  CLIENTE_id_cliente: z.coerce.number().positive("Cliente é obrigatório"),
  BARBEIRO_id_barbeiro: z.coerce.number().positive("Barbeiro é obrigatório"),
  data_hora: z.string().min(1, "Data e hora são obrigatórias"),
  observacao: z.string(),
  servicoIds: z.array(z.coerce.number()).min(1, "Selecione ao menos um serviço")
});

export type AtendimentoFormInput = z.input<typeof atendimentoFormSchema>;
export type AtendimentoFormValues = z.output<typeof atendimentoFormSchema>;

export const defaultAtendimentoFormValues: AtendimentoFormValues = {
  CLIENTE_id_cliente: 0,
  BARBEIRO_id_barbeiro: 0,
  data_hora: "",
  observacao: "",
  servicoIds: []
};
