import { VendaDetail } from "@/components/vendas/VendaDetail";

export default async function VendaDetailPage({
  params
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return <VendaDetail vendaId={Number(id)} />;
}
