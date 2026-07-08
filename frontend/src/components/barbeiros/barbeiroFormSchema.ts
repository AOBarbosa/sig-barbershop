import { z } from "zod";

export const barbeiroFormSchema = z.object({
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
  comissao_percentual: z.coerce.number().min(0).max(100).nullable()
});

export type BarbeiroFormInput = z.input<typeof barbeiroFormSchema>;
export type BarbeiroFormValues = z.output<typeof barbeiroFormSchema>;

export const defaultBarbeiroFormValues: BarbeiroFormInput = {
  nome: "",
  cpf: "",
  email: "",
  data_nascimento: "",
  apelido: "",
  comissao_percentual: null
};
