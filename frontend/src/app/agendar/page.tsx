import { Suspense } from "react";

import { AgendamentoPublico } from "@/components/agendamento/AgendamentoPublico";

export default function AgendarPage() {
  return (
    <Suspense>
      <AgendamentoPublico />
    </Suspense>
  );
}
