"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, LockKeyhole } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/useAuth";

const loginFormSchema = z.object({
  email: z.string().trim().min(1, "Email é obrigatório"),
  senha: z.string().min(1, "Senha é obrigatória")
});

type LoginFormValues = z.infer<typeof loginFormSchema>;

function getSafeNext(next: string | null) {
  if (!next || !next.startsWith("/") || next.startsWith("//")) {
    return "/";
  }

  return next;
}

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const auth = useAuth();
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginFormSchema),
    defaultValues: {
      email: "",
      senha: ""
    }
  });
  const isSubmitting = form.formState.isSubmitting;

  async function onSubmit(values: LoginFormValues) {
    try {
      await auth.login(values);
      router.push(getSafeNext(searchParams.get("next")));
    } catch {
      // erro exibido via auth.loginError
    }
  }

  return (
    <main className="bg-background flex min-h-screen items-center justify-center px-4 py-8">
      <Card className="w-full max-w-md">
        <CardHeader>
          <div className="bg-muted flex size-10 items-center justify-center rounded-lg">
            <LockKeyhole className="size-5" />
          </div>
          <CardTitle>Entrar no SIG Barbershop</CardTitle>
          <CardDescription>
            Use seu email e senha para acessar o painel operacional.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form
              onSubmit={form.handleSubmit(onSubmit)}
              className="space-y-4"
              noValidate>
              <FormField name="email">
                {(field) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        type="email"
                        autoComplete="email"
                        placeholder="voce@barbearia.com"
                      />
                    </FormControl>
                    <FormMessage>
                      {form.formState.errors.email?.message}
                    </FormMessage>
                  </FormItem>
                )}
              </FormField>
              <FormField name="senha">
                {(field) => (
                  <FormItem>
                    <FormLabel>Senha</FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        type="password"
                        autoComplete="current-password"
                      />
                    </FormControl>
                    <FormMessage>
                      {form.formState.errors.senha?.message}
                    </FormMessage>
                  </FormItem>
                )}
              </FormField>
              {auth.loginError ? (
                <Alert variant="destructive">
                  <AlertTitle>Não foi possível entrar</AlertTitle>
                  <AlertDescription>{auth.loginError.message}</AlertDescription>
                </Alert>
              ) : null}
              <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? (
                  <Loader2 className="size-4 animate-spin" />
                ) : null}
                Entrar
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
    </main>
  );
}
