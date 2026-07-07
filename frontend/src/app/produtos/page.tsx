import { Suspense } from "react";

import { ProdutosList } from "@/components/produtos/ProdutosList";
import { Skeleton } from "@/components/ui/skeleton";

function ProdutosFallback() {
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

export default function ProdutosPage() {
  return (
    <Suspense fallback={<ProdutosFallback />}>
      <ProdutosList />
    </Suspense>
  );
}
