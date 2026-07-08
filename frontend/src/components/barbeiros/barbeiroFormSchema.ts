import { z } from "zod";

const disponibilidadeSchema = z
  .object({
    dia_semana: z.string().min(1, "Dia da semana é obrigatório"),
    hora_inicio: z.string().min(1, "Hora inicial é obrigatória"),
    hora_fim: z.string().min(1, "Hora final é obrigatória")
  })
  .refine((value) => value.hora_fim > value.hora_inicio, {
    message: "Fim deve ser posterior ao início",
    path: ["hora_fim"]
  });

function hasConflito(
  disponibilidades: z.infer<typeof disponibilidadeSchema>[]
) {
  return disponibilidades.some((disponibilidade, index) =>
    disponibilidades.some(
      (outra, outroIndex) =>
        index !== outroIndex &&
        disponibilidade.dia_semana === outra.dia_semana &&
        disponibilidade.hora_inicio < outra.hora_fim &&
        outra.hora_inicio < disponibilidade.hora_fim
    )
  );
}

export const barbeiroFormSchema = z
  .object({
    nome: z.string().trim().min(1, "Nome é obrigatório"),
    cpf: z
      .string()
      .trim()
      .regex(/^\d{11}$/, "CPF deve conter 11 dígitos"),
    email: z
      .string()
      .trim()
      .regex(/^([^\s@]+@[^\s@]+\.[^\s@]+)?$/, "Email inválido")
      .transform((value) => (value === "" ? null : value)),
    data_nascimento: z
      .string()
      .trim()
      .or(z.literal(""))
      .transform((value) => (value === "" ? null : value)),
    apelido: z
      .string()
      .trim()
      .or(z.literal(""))
      .transform((value) => (value === "" ? null : value)),
    comissao_percentual: z.coerce.number().min(0).max(100).nullable(),
    disponibilidades: z
      .array(disponibilidadeSchema)
      .min(1, "Informe ao menos uma disponibilidade")
  })
  .superRefine((value, context) => {
    if (hasConflito(value.disponibilidades)) {
      context.addIssue({
        code: "custom",
        message: "Existem horários sobrepostos no mesmo dia",
        path: ["disponibilidades"]
      });
    }
  });

export type BarbeiroFormInput = z.input<typeof barbeiroFormSchema>;
export type BarbeiroFormValues = z.output<typeof barbeiroFormSchema>;

export const defaultBarbeiroFormValues: BarbeiroFormInput = {
  nome: "",
  cpf: "",
  email: "",
  data_nascimento: "",
  apelido: "",
  comissao_percentual: null,
  disponibilidades: [
    {
      dia_semana: "SEGUNDA",
      hora_inicio: "",
      hora_fim: ""
    }
  ]
};
