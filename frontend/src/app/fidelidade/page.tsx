import { Suspense } from "react";

import { FidelidadeList } from "@/components/fidelidade/FidelidadeList";
import { Skeleton } from "@/components/ui/skeleton";

function FidelidadeFallback() {
  return (
    <section className="space-y-5">
      <Skeleton className="h-16 w-full" />
      <div className="grid gap-4 md:grid-cols-2">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
      <Skeleton className="h-80 w-full" />
    </section>
  );
}

export default function FidelidadePage() {
  return (
    <Suspense fallback={<FidelidadeFallback />}>
      <FidelidadeList />
    </Suspense>
  );
}
