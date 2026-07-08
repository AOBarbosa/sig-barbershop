import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export function AtendimentoErrorAlert({ message }: { message?: string }) {
  if (!message) {
    return null;
  }

  return (
    <Alert variant="destructive">
      <AlertTitle>Erro ao salvar atendimento</AlertTitle>
      <AlertDescription>{message}</AlertDescription>
    </Alert>
  );
}
