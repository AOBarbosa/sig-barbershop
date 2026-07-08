import { Suspense } from "react";
import Link from "next/link";
import { CalendarClock, MapPin, Scissors, Star } from "lucide-react";

import { AgendamentoPublico } from "@/components/agendamento/AgendamentoPublico";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const servicos = ["Corte masculino", "Barba completa", "Acabamento", "Pacotes"];

export default function PublicHomePage() {
  return (
    <main className="bg-background min-h-screen">
      <header className="absolute inset-x-0 top-0 z-20">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
          <Link href="/" className="text-sm font-semibold text-white">
            O Teu Barbeiro
          </Link>
          <div className="flex items-center gap-2">
            <Button asChild size="sm" variant="secondary">
              <Link href="#agendar">Agendar</Link>
            </Button>
            <Button asChild size="sm" variant="outline">
              <Link href="/login">Entrar</Link>
            </Button>
          </div>
        </div>
      </header>

      <section className="relative flex min-h-[88vh] items-end overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage:
              "url('https://images.unsplash.com/photo-1621605815971-fbc98d665033?auto=format&fit=crop&w=1800&q=85')"
          }}
          aria-label="Barbearia com cadeira e espelho"
        />
        <div className="absolute inset-0 bg-black/60" />
        <div className="relative mx-auto grid w-full max-w-6xl gap-8 px-4 pt-28 pb-16 text-white md:grid-cols-[1fr_22rem] md:items-end">
          <div className="max-w-2xl space-y-5">
            <Badge className="bg-white/15 text-white">Barbearia premium</Badge>
            <h1 className="text-4xl font-semibold tracking-tight md:text-6xl">
              Seu próximo corte começa pelo horário certo.
            </h1>
            <p className="max-w-xl text-base text-white/80">
              Escolha um barbeiro, veja os horários livres e reserve sem entrar
              no painel da equipe.
            </p>
            <div className="flex flex-col gap-3 sm:flex-row">
              <Button asChild size="lg">
                <Link href="#agendar">Ver horários</Link>
              </Button>
              <Button asChild size="lg" variant="secondary">
                <Link href="/login">Já tenho conta</Link>
              </Button>
            </div>
          </div>

          <div className="grid gap-3 rounded-lg border border-white/20 bg-black/35 p-4 text-sm backdrop-blur">
            <p className="font-medium">Atendimento por agendamento</p>
            <p className="flex items-center gap-2 text-white/80">
              <CalendarClock className="size-4" />
              Horários livres em tempo real
            </p>
            <p className="flex items-center gap-2 text-white/80">
              <Scissors className="size-4" />
              Barbeiros selecionados
            </p>
            <p className="flex items-center gap-2 text-white/80">
              <MapPin className="size-4" />
              Experiência simples para o cliente
            </p>
          </div>
        </div>
      </section>

      <section className="border-b">
        <div className="mx-auto grid max-w-6xl gap-4 px-4 py-8 md:grid-cols-4">
          {servicos.map((servico) => (
            <div key={servico} className="flex items-center gap-3">
              <div className="bg-muted flex size-9 items-center justify-center rounded-lg">
                <Star className="size-4" />
              </div>
              <p className="text-sm font-medium">{servico}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="agendar" className="mx-auto max-w-6xl px-4 py-10">
        <Suspense>
          <AgendamentoPublico publicHome />
        </Suspense>
      </section>
    </main>
  );
}
