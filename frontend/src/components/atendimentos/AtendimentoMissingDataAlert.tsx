import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export function AtendimentoMissingDataAlert({ message }: { message: string }) {
  return (
    <Alert variant="destructive">
      <AlertTitle>Dados não encontrados</AlertTitle>
      <AlertDescription>{message}</AlertDescription>
    </Alert>
  );
}
