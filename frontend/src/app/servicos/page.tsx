import { Suspense } from "react";

import { ServicosList } from "@/components/servicos/ServicosList";
import { Skeleton } from "@/components/ui/skeleton";

function ServicosFallback() {
  return (
    <div className="space-y-5">
      <Skeleton className="h-20 w-full" />
      <div className="grid gap-4 md:grid-cols-3">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
      <Skeleton className="h-96 w-full" />
    </div>
  );
}

export default function ServicosPage() {
  return (
    <Suspense fallback={<ServicosFallback />}>
      <ServicosList />
    </Suspense>
  );
}
