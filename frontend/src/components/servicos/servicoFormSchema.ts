import { z } from "zod";

export const servicoFormSchema = z.object({
  nome: z.string().trim().min(1, "Nome é obrigatório"),
  preco: z.coerce.number().min(0, "Preço deve ser positivo"),
  duracao_em_minutos: z.coerce.number().int().positive("Duração é obrigatória"),
  pontos_gerados: z.coerce.number().int().min(0, "Pontos deve ser positivo"),
  ativo: z.boolean()
});

export type ServicoFormInput = z.input<typeof servicoFormSchema>;
export type ServicoFormValues = z.output<typeof servicoFormSchema>;

export const defaultServicoFormValues: ServicoFormInput = {
  nome: "",
  preco: 0,
  duracao_em_minutos: 30,
  pontos_gerados: 0,
  ativo: true
};
