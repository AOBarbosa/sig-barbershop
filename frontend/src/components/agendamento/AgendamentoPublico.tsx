"use client";

import { CalendarCheck, Scissors } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from "@/components/ui/card";
import { useAgendamentoPublicoState } from "@/components/agendamento/useAgendamentoPublicoState";
import { useAuth } from "@/hooks/useAuth";
import { useCreateAtendimentoCliente } from "@/hooks/useAtendimentos";

export function AgendamentoPublico({
  publicHome = false
}: {
  publicHome?: boolean;
}) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const auth = useAuth();
  const createAtendimento = useCreateAtendimentoCliente();
  const initialBarbeiro = Number(searchParams.get("barbeiro") ?? 0);
  const initialHorario = searchParams.get("horario") ?? "";
  const [confirmed, setConfirmed] = useState(false);
  const state = useAgendamentoPublicoState(initialBarbeiro, initialHorario);
  const selectedBarbeiro = state.barbeiros.find(
    (item) => item.PESSOA_id_pessoa === state.barbeiroId
  );
  const selectedHorario = useMemo(
    () => state.horarios.find((item) => item.value === state.horario),
    [state.horario, state.horarios]
  );

  async function confirmar() {
    const next = `/?barbeiro=${state.barbeiroId}&horario=${state.horario}`;

    if (!auth.user) {
      router.push(`/login?next=${encodeURIComponent(next)}`);
      return;
    }

    await createAtendimento.mutateAsync({
      CLIENTE_PESSOA_id_pessoa: auth.user.id_pessoa,
      BARBEIRO_PESSOA_id_pessoa: state.barbeiroId,
      data_hora_inicio: state.horario,
      status: "AGENDADO",
      observacoes: "Agendamento público"
    });
    setConfirmed(true);
  }

  return (
    <section className="space-y-6">
      <div className="space-y-2">
        <Badge variant="secondary">Agenda pública</Badge>
        <h2 className="text-3xl font-semibold tracking-tight">
          Agendar horário
        </h2>
        <p className="text-muted-foreground max-w-2xl text-sm">
          {publicHome
            ? "Veja os barbeiros e horários livres antes de entrar ou criar sua conta."
            : "Escolha um barbeiro e um horário disponível. O login só será pedido para confirmar o agendamento."}
        </p>
      </div>

      {confirmed ? (
        <Alert>
          <CalendarCheck className="size-4" />
          <AlertTitle>Agendamento confirmado</AlertTitle>
          <AlertDescription>
            Seu horário foi registrado com sucesso.
          </AlertDescription>
        </Alert>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-[1fr_20rem]">
        <Card>
          <CardHeader>
            <CardTitle>Barbeiros disponíveis</CardTitle>
            <CardDescription>
              Selecione quem irá realizar o atendimento.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3 md:grid-cols-2">
            {state.barbeiros.map((barbeiro) => (
              <Button
                key={barbeiro.PESSOA_id_pessoa}
                variant={
                  barbeiro.PESSOA_id_pessoa === state.barbeiroId
                    ? "default"
                    : "outline"
                }
                className="h-auto justify-start gap-3 p-3"
                onClick={() => state.selectBarbeiro(barbeiro.PESSOA_id_pessoa)}>
                <Scissors className="size-4" />
                <span className="text-left">
                  <span className="block">{barbeiro.pessoa.nome}</span>
                  <span className="text-xs opacity-80">
                    {barbeiro.apelido ?? "Barbeiro"}
                  </span>
                </span>
              </Button>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Revisar agendamento</CardTitle>
            <CardDescription>
              Confirme os dados antes de concluir.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm">
              Barbeiro: {selectedBarbeiro?.pessoa.nome ?? "Selecione"}
            </p>
            <p className="text-sm">
              Horário: {selectedHorario?.label ?? "Selecione"}
            </p>
            <Button
              className="w-full"
              disabled={!state.barbeiroId || !state.horario}
              onClick={confirmar}>
              Confirmar agendamento
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Horários disponíveis</CardTitle>
          <CardDescription>
            Os horários ocupados não aparecem nesta lista.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {state.horarios.map((horario) => (
            <Button
              key={horario.value}
              variant={horario.value === state.horario ? "default" : "outline"}
              onClick={() => state.selectHorario(horario.value)}>
              {horario.label}
            </Button>
          ))}
        </CardContent>
      </Card>
    </section>
  );
}
