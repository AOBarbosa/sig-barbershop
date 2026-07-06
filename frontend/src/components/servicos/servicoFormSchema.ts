import { z } from "zod";

export const servicoFormSchema = z.object({
  nome: z.string().trim().min(1, "Nome é obrigatório"),
  descricao: z.string(),
  preco: z.coerce.number().positive("Preço deve ser maior que zero"),
  duracao_minutos: z.coerce
    .number()
    .int("Duração deve ser um número inteiro")
    .positive("Duração deve ser maior que zero"),
  ativo: z.boolean()
});

export type ServicoFormInput = z.input<typeof servicoFormSchema>;
export type ServicoFormValues = z.output<typeof servicoFormSchema>;

export const defaultServicoFormValues: ServicoFormInput = {
  nome: "",
  descricao: "",
  preco: 0,
  duracao_minutos: 30,
  ativo: true
};
