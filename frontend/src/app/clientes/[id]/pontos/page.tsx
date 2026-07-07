import { ClientePontos } from "@/components/fidelidade/ClientePontos";

interface ClientePontosPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function ClientePontosPage({
  params
}: ClientePontosPageProps) {
  const { id } = await params;

  return <ClientePontos clienteId={Number(id)} />;
}
