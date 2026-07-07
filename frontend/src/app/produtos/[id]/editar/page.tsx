import { ProdutoForm } from "@/components/produtos/ProdutoForm";

interface EditarProdutoPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function EditarProdutoPage({
  params
}: EditarProdutoPageProps) {
  const { id } = await params;

  return <ProdutoForm mode="edit" produtoId={Number(id)} />;
}
