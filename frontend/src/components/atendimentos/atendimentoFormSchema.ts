import { z } from "zod";

export const atendimentoFormSchema = z.object({
  CLIENTE_PESSOA_id_pessoa: z.coerce.number().positive("Cliente é obrigatório"),
  BARBEIRO_PESSOA_id_pessoa: z.coerce
    .number()
    .positive("Barbeiro é obrigatório"),
  data_hora_inicio: z.string().min(1, "Data e hora são obrigatórias"),
  observacoes: z.string(),
  servicoIds: z.array(z.coerce.number()).min(1, "Selecione ao menos um serviço")
});

export type AtendimentoFormInput = z.input<typeof atendimentoFormSchema>;
export type AtendimentoFormValues = z.output<typeof atendimentoFormSchema>;

export const defaultAtendimentoFormValues: AtendimentoFormValues = {
  CLIENTE_PESSOA_id_pessoa: 0,
  BARBEIRO_PESSOA_id_pessoa: 0,
  data_hora_inicio: "",
  observacoes: "",
  servicoIds: []
};
