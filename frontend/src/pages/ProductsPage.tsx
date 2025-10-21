import React, { useMemo, useState } from 'react';
import { useProducts, useCreateProduct, useUpdateProduct, useDeleteProduct } from '../hooks/useProducts';
import { useCategories } from '../hooks/useCategories';
import type { Product, ProductCreate, ProductFilter } from '../types/product';
import type { Category } from '../types/category';
import { Modal } from '../components/ui/Modal';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';

interface ProductFormProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
  categories: Category[];
  initial?: Partial<Product>;
}

const ProductForm: React.FC<ProductFormProps> = ({ open, onClose, onSubmit, categories, initial }) => {
  const [form, setForm] = useState<Partial<ProductCreate>>({
    name: initial?.name || '',
    sku: initial?.sku || '',
    description: initial?.description || '',
    quantity: initial?.quantity ?? 0,
    min_quantity: initial?.min_quantity ?? undefined,
    max_quantity: initial?.max_quantity ?? undefined,
    price: (initial as any)?.price ?? 0,
    category_id: initial?.category_id || '',
    unit: initial?.unit || '',
    location: initial?.location || '',
    status: (initial?.status as any) || 'active',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: name.includes('quantity') || name === 'price' ? Number(value) : value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(form as ProductCreate);
  };

  return (
    <Modal isOpen={open} onClose={onClose} title={initial?.id ? 'Editar Produto' : 'Novo Produto'} size="lg" footer={null}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input label="Nome" name="name" value={form.name || ''} onChange={handleChange} required />
          <Input label="SKU" name="sku" value={form.sku || ''} onChange={handleChange} required />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input type="number" min={0} label="Quantidade" name="quantity" value={form.quantity ?? 0} onChange={handleChange} required />
          <Input type="number" min={0} label="Qtd Mínima" name="min_quantity" value={form.min_quantity ?? ''} onChange={handleChange} />
          <Input type="number" min={0} label="Qtd Máxima" name="max_quantity" value={form.max_quantity ?? ''} onChange={handleChange} />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input type="number" step="0.01" min={0} label="Preço" name="price" value={(form.price as number) ?? 0} onChange={handleChange} required />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
            <select name="category_id" className="w-full border rounded-md px-3 py-2" value={form.category_id || ''} onChange={handleChange}>
              <option value="">Sem categoria</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select name="status" className="w-full border rounded-md px-3 py-2" value={(form.status as any) || 'active'} onChange={handleChange}>
              <option value="active">Ativo</option>
              <option value="inactive">Inativo</option>
            </select>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input label="Unidade" name="unit" value={form.unit || ''} onChange={handleChange} />
          <Input label="Localização" name="location" value={form.location || ''} onChange={handleChange} />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Descrição</label>
          <textarea name="description" className="w-full border rounded-md px-3 py-2" value={form.description || ''} onChange={handleChange} rows={3} />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button type="button" variant="secondary" onClick={onClose}>Cancelar</Button>
          <Button type="submit">Salvar</Button>
        </div>
      </form>
    </Modal>
  );
};

export const ProductsPage: React.FC = () => {
  const [filters, setFilters] = useState<ProductFilter>({ page: 1, page_size: 10, sort_by: 'created_at', sort_order: 'desc' });
  const [createOpen, setCreateOpen] = useState(false);
  const [editItem, setEditItem] = useState<Product | null>(null);

  const { data: categoriesData } = useCategories({ limit: 100 });
  const categories = useMemo(() => categoriesData?.items ?? [], [categoriesData]);

  const { data, isLoading, isError, refetch } = useProducts(filters);
  const createMutation = useCreateProduct();
  const updateMutation = useUpdateProduct();
  const deleteMutation = useDeleteProduct();

  const onCreate = async (payload: ProductCreate) => {
    await createMutation.mutateAsync(payload);
    setCreateOpen(false);
  };

  const onUpdate = async (payload: Partial<Product>) => {
    if (!editItem) return;
    await updateMutation.mutateAsync({ id: editItem.id, data: payload });
    setEditItem(null);
  };

  const onDelete = async (item: Product) => {
    if (confirm(`Excluir produto ${item.name}?`)) {
      await deleteMutation.mutateAsync(item.id);
    }
  };

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, page: 1, [name]: value }));
  };

  const pages = data?.pages ?? 1;
  const items = data?.items ?? [];

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-semibold text-gray-900">Produtos</h1>
        <Button onClick={() => setCreateOpen(true)}>Novo Produto</Button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-4">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          <Input label="Nome" name="name" value={filters.name || ''} onChange={handleFilterChange} />
          <Input label="SKU" name="sku" value={filters.sku || ''} onChange={handleFilterChange} />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
            <select name="category_id" className="w-full border rounded-md px-3 py-2" value={filters.category_id || ''} onChange={handleFilterChange}>
              <option value="">Todas</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select name="status" className="w-full border rounded-md px-3 py-2" value={filters.status || ''} onChange={handleFilterChange}>
              <option value="">Todos</option>
              <option value="active">Ativo</option>
              <option value="inactive">Inativo</option>
            </select>
          </div>
          <div className="flex items-end gap-2">
            <Button variant="secondary" onClick={() => refetch()}>Filtrar</Button>
            <Button variant="ghost" onClick={() => setFilters({ page: 1, page_size: 10, sort_by: 'created_at', sort_order: 'desc' })}>Limpar</Button>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nome</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SKU</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Qtd</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Preço</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3"></th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {isLoading && (
              <tr><td className="px-6 py-4" colSpan={6}>Carregando...</td></tr>
            )}
            {isError && (
              <tr><td className="px-6 py-4 text-red-600" colSpan={6}>Erro ao carregar produtos.</td></tr>
            )}
            {!isLoading && !isError && items.length === 0 && (
              <tr><td className="px-6 py-4" colSpan={6}>Nenhum produto encontrado.</td></tr>
            )}
            {items.map((p) => (
              <tr key={p.id}>
                <td className="px-6 py-3 whitespace-nowrap">{p.name}</td>
                <td className="px-6 py-3 whitespace-nowrap">{p.sku}</td>
                <td className="px-6 py-3 whitespace-nowrap">{p.quantity}</td>
                <td className="px-6 py-3 whitespace-nowrap">R$ {Number(p.price).toFixed(2)}</td>
                <td className="px-6 py-3 whitespace-nowrap">
                  <span className={`px-2 py-1 rounded text-xs ${p.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
                    {p.status === 'active' ? 'Ativo' : 'Inativo'}
                  </span>
                </td>
                <td className="px-6 py-3 text-right whitespace-nowrap flex gap-2 justify-end">
                  <Button variant="secondary" onClick={() => setEditItem(p)}>Editar</Button>
                  <Button variant="danger" onClick={() => onDelete(p)}>Excluir</Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Pagination */}
        <div className="flex items-center justify-between px-4 py-3 border-t">
          <div className="text-sm text-gray-600">Total: {data?.total ?? 0}</div>
          <div className="flex gap-2">
            <Button variant="secondary" disabled={(filters.page ?? 1) <= 1} onClick={() => setFilters((f) => ({ ...f, page: (f.page ?? 1) - 1 }))}>Anterior</Button>
            <span className="px-2 py-2 text-sm">Página {filters.page ?? 1} de {pages}</span>
            <Button variant="secondary" disabled={(filters.page ?? 1) >= pages} onClick={() => setFilters((f) => ({ ...f, page: (f.page ?? 1) + 1 }))}>Próxima</Button>
          </div>
        </div>
      </div>

      {/* Create Modal */}
      <ProductForm open={createOpen} onClose={() => setCreateOpen(false)} onSubmit={onCreate} categories={categories} />

      {/* Edit Modal */}
      {editItem && (
        <ProductForm open={!!editItem} onClose={() => setEditItem(null)} onSubmit={onUpdate} categories={categories} initial={editItem} />
      )}
    </div>
  );
};
