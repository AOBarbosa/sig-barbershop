import { z } from "zod";

export const clienteFormSchema = z.object({
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
    .transform((value) => (value === "" ? null : value))
});

export type ClienteFormInput = z.input<typeof clienteFormSchema>;
export type ClienteFormValues = z.output<typeof clienteFormSchema>;

export const defaultClienteFormValues: ClienteFormInput = {
  nome: "",
  cpf: "",
  email: "",
  data_nascimento: ""
};
