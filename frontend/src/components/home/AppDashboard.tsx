import { CalendarClock, Scissors, ShoppingCart } from "lucide-react";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from "@/components/ui/card";

const overview = [
  {
    title: "Serviços",
    description: "Catálogo de cortes, barba e pacotes.",
    href: "/servicos",
    icon: Scissors
  },
  {
    title: "Atendimentos",
    description: "Agenda e acompanhamento de horários.",
    href: "/atendimentos",
    icon: CalendarClock
  },
  {
    title: "Vendas",
    description: "Produtos e fluxo de caixa operacional.",
    href: "/vendas",
    icon: ShoppingCart
  }
];

export function AppDashboard() {
  return (
    <section className="space-y-6">
      <div className="space-y-2">
        <Badge variant="secondary">Painel</Badge>
        <h1 className="text-3xl font-semibold tracking-tight">
          Operação da barbearia
        </h1>
        <p className="text-muted-foreground max-w-2xl text-sm">
          Acompanhe os módulos principais do sistema e acesse rapidamente os
          cadastros usados nos atendimentos.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {overview.map((item) => {
          const Icon = item.icon;

          return (
            <Card key={item.href}>
              <CardHeader>
                <div className="bg-muted flex size-9 items-center justify-center rounded-lg">
                  <Icon className="size-4" />
                </div>
                <CardTitle>{item.title}</CardTitle>
                <CardDescription>{item.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Button asChild variant="outline">
                  <Link href={item.href}>Acessar</Link>
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </section>
  );
}
