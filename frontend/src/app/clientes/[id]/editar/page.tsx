import { ClienteForm } from "@/components/clientes/ClienteForm";

interface EditarClientePageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function EditarClientePage({
  params
}: EditarClientePageProps) {
  const { id } = await params;

  return <ClienteForm mode="edit" clienteId={Number(id)} />;
}
