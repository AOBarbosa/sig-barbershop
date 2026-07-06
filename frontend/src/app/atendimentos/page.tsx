import { Suspense } from "react";

import { AtendimentosList } from "@/components/atendimentos/AtendimentosList";
import { Skeleton } from "@/components/ui/skeleton";

function AtendimentosFallback() {
  return (
    <section className="space-y-5">
      <Skeleton className="h-16 w-full" />
      <div className="grid gap-4 md:grid-cols-3">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
      <Skeleton className="h-80 w-full" />
    </section>
  );
}

export default function AtendimentosPage() {
  return (
    <Suspense fallback={<AtendimentosFallback />}>
      <AtendimentosList />
    </Suspense>
  );
}
