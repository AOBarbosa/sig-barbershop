import { Suspense } from "react";

import { VendasList } from "@/components/vendas/VendasList";
import { Skeleton } from "@/components/ui/skeleton";

function VendasFallback() {
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

export default function VendasPage() {
  return (
    <Suspense fallback={<VendasFallback />}>
      <VendasList />
    </Suspense>
  );
}
