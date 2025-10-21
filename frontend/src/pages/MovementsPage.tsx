import { useState } from 'react';
import { useMovements, useCreateMovement } from '../hooks/useMovements';
import { useProductsMini } from '../hooks/useProductsMini';
import { useProductsMap } from '../hooks/useProductsMap';
import { MovementCreate } from '../types/movement';
type MovementType = 'entry' | 'exit' | 'adjustment';

const movementTypeLabels: Record<MovementType, string> = {
  entry: 'Entrada',
  exit: 'Saída',
  adjustment: 'Ajuste',
};

export default function MovementsPage() {
  const [filters, setFilters] = useState({ page: 1, page_size: 20 });
  const { data, isLoading, error } = useMovements(filters);
  const createMovement = useCreateMovement();

  // Form state
  const [form, setForm] = useState<Partial<MovementCreate>>({ type: 'entry' });
  const [showForm, setShowForm] = useState(false);
  const [productQuery, setProductQuery] = useState('');
  const [selectedProduct, setSelectedProduct] = useState<{ id: string; sku: string; name: string } | null>(null);
  const { data: productOptions, isLoading: loadingProducts } = useProductsMini(productQuery);

  function handleInputChange(e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  }

  function handleProductSearch(e: React.ChangeEvent<HTMLInputElement>) {
    setProductQuery(e.target.value);
    setSelectedProduct(null);
    setForm((f) => ({ ...f, product_id: undefined }));
  }

  function handleProductSelect(p: { id: string; sku: string; name: string }) {
    setSelectedProduct(p);
    setForm((f) => ({ ...f, product_id: p.id }));
    setProductQuery(`${p.sku} - ${p.name}`);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.product_id || !form.type || !form.quantity) return;
    createMovement.mutate({
      product_id: form.product_id,
      type: form.type as MovementType,
      quantity: Number(form.quantity),
      reason: form.reason,
      notes: form.notes,
    } as MovementCreate, {
      onSuccess: () => {
        setShowForm(false);
        setForm({ type: 'entry' });
        setProductQuery('');
        setSelectedProduct(null);
      },
    });
  }

  // Obter todos os product_ids exibidos na página
  const productIds = data?.items.map((m) => m.product_id) || [];
  const { data: productsMap } = useProductsMap(productIds);

  return (
    <div className="p-4 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Movimentações de Estoque</h1>
      <button
        className="mb-4 px-4 py-2 bg-blue-600 text-white rounded"
        onClick={() => setShowForm((v) => !v)}
      >
        {showForm ? 'Cancelar' : 'Nova Movimentação'}
      </button>
      {showForm && (
        <form className="mb-6 p-4 border rounded bg-gray-50" onSubmit={handleSubmit}>
          <div className="mb-2">
            <label className="block mb-1">Produto</label>
            <input
              type="text"
              placeholder="Busque por SKU ou nome"
              value={productQuery}
              onChange={handleProductSearch}
              className="border px-2 py-1 rounded w-full"
              autoComplete="off"
              required
            />
            {productQuery && !selectedProduct && (
              <div className="border rounded bg-white shadow max-h-40 overflow-y-auto absolute z-10 w-full">
                {loadingProducts && <div className="p-2 text-gray-500">Carregando...</div>}
                {productOptions?.length === 0 && !loadingProducts && (
                  <div className="p-2 text-gray-500">Nenhum produto encontrado</div>
                )}
                {productOptions?.map((p) => (
                  <div
                    key={p.id}
                    className="p-2 hover:bg-blue-100 cursor-pointer"
                    onClick={() => handleProductSelect(p)}
                  >
                    <span className="font-mono text-xs bg-gray-100 px-1 rounded mr-2">{p.sku}</span>
                    {p.name}
                  </div>
                ))}
              </div>
            )}
            {selectedProduct && (
              <div className="text-xs text-gray-600 mt-1">
                Selecionado: <span className="font-mono bg-gray-100 px-1 rounded">{selectedProduct.sku}</span> {selectedProduct.name}
              </div>
            )}
          </div>
          <div className="mb-2">
            <label className="block mb-1">Tipo</label>
            <select
              name="type"
              value={form.type}
              onChange={handleInputChange}
              className="border px-2 py-1 rounded w-full"
              required
            >
              <option value="entry">Entrada</option>
              <option value="exit">Saída</option>
              <option value="adjustment">Ajuste</option>
            </select>
          </div>
          <div className="mb-2">
            <label className="block mb-1">Quantidade</label>
            <input
              name="quantity"
              type="number"
              min={1}
              value={form.quantity || ''}
              onChange={handleInputChange}
              className="border px-2 py-1 rounded w-full"
              required
            />
          </div>
          <div className="mb-2">
            <label className="block mb-1">Motivo</label>
            <input
              name="reason"
              value={form.reason || ''}
              onChange={handleInputChange}
              className="border px-2 py-1 rounded w-full"
            />
          </div>
          <div className="mb-2">
            <label className="block mb-1">Observações</label>
            <input
              name="notes"
              value={form.notes || ''}
              onChange={handleInputChange}
              className="border px-2 py-1 rounded w-full"
            />
          </div>
          <button
            type="submit"
            className="mt-2 px-4 py-2 bg-green-600 text-white rounded"
            disabled={createMovement.status === 'pending'}
          >
            Salvar
          </button>
        </form>
      )}
      {isLoading && <div>Carregando...</div>}
      {error && <div className="text-red-600">Erro: {error.message}</div>}
      <table className="w-full border mt-4">
        <thead>
          <tr className="bg-gray-100">
            <th className="p-2 border">Data</th>
            <th className="p-2 border">Produto</th>
            <th className="p-2 border">Tipo</th>
            <th className="p-2 border">Delta</th>
            <th className="p-2 border">Saldo Após</th>
            <th className="p-2 border">Motivo</th>
            <th className="p-2 border">Usuário</th>
          </tr>
        </thead>
        <tbody>
          {data?.items.map((m) => {
            const prod = productsMap?.[m.product_id];
            return (
              <tr key={m.id}>
                <td className="p-2 border">{new Date(m.created_at).toLocaleString()}</td>
                <td className="p-2 border">
                  {prod ? (
                    <>
                      <span className="font-mono text-xs bg-gray-100 px-1 rounded mr-2">{prod.sku}</span>
                      {prod.name}
                    </>
                  ) : (
                    <span className="text-gray-400">{m.product_id}</span>
                  )}
                </td>
                <td className="p-2 border">{movementTypeLabels[m.type]}</td>
                <td className="p-2 border">{m.quantity > 0 ? '+' : ''}{m.quantity}</td>
                <td className="p-2 border">{m.balance_after}</td>
                <td className="p-2 border">{m.reason}</td>
                <td className="p-2 border">{m.user_id}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <div className="mt-4 flex gap-2 items-center">
        <button
          className="px-2 py-1 border rounded"
          disabled={filters.page === 1}
          onClick={() => setFilters((f) => ({ ...f, page: (f.page || 1) - 1 }))}
        >
          Anterior
        </button>
        <span>Página {data?.page} de {data?.pages}</span>
        <button
          className="px-2 py-1 border rounded"
          disabled={!!data && data.page === data.pages}
          onClick={() => setFilters((f) => ({ ...f, page: (f.page || 1) + 1 }))}
        >
          Próxima
        </button>
      </div>
    </div>
  );
}
