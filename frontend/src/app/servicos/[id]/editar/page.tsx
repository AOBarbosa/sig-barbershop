import { ServicoForm } from "@/components/servicos/ServicoForm";

interface EditarServicoPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function EditarServicoPage({
  params
}: EditarServicoPageProps) {
  const { id } = await params;

  return <ServicoForm mode="edit" servicoId={Number(id)} />;
}
