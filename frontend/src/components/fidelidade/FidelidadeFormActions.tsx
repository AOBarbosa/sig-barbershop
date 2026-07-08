import { Loader2 } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";

export function FidelidadeFormActions({ loading }: { loading: boolean }) {
  return (
    <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
      <Button asChild variant="outline" type="button">
        <Link href="/fidelidade">Cancelar</Link>
      </Button>
      <Button type="submit" disabled={loading}>
        {loading ? <Loader2 className="size-4 animate-spin" /> : null}
        Salvar regra
      </Button>
    </div>
  );
}
