import { Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";

export function VendaSubmitButton({ loading }: { loading: boolean }) {
  return (
    <Button type="submit" disabled={loading}>
      {loading ? <Loader2 className="size-4 animate-spin" /> : null}
      Salvar venda
    </Button>
  );
}
