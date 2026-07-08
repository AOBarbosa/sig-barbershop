import { Suspense } from "react";

import { ClientesList } from "@/components/clientes/ClientesList";
import { Skeleton } from "@/components/ui/skeleton";

function ClientesFallback() {
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

export default function ClientesPage() {
  return (
    <Suspense fallback={<ClientesFallback />}>
      <ClientesList />
    </Suspense>
  );
}
