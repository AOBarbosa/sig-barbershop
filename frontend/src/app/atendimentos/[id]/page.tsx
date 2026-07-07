import { AtendimentoDetail } from "@/components/atendimentos/AtendimentoDetail";

export default async function AtendimentoDetailPage({
  params
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return <AtendimentoDetail atendimentoId={Number(id)} />;
}
