import { BarbeiroForm } from "@/components/barbeiros/BarbeiroForm";

interface EditarBarbeiroPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function EditarBarbeiroPage({
  params
}: EditarBarbeiroPageProps) {
  const { id } = await params;

  return <BarbeiroForm mode="edit" barbeiroId={Number(id)} />;
}
