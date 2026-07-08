import { FidelidadeForm } from "@/components/fidelidade/FidelidadeForm";

interface EditarFidelidadePageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function EditarFidelidadePage({
  params
}: EditarFidelidadePageProps) {
  const { id } = await params;

  return <FidelidadeForm mode="edit" fidelidadeId={Number(id)} />;
}
