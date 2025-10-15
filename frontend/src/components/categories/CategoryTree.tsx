/**
 * CategoryTree Component
 * 
 * Renders a hierarchical tree of categories with expand/collapse,
 * selection, and optional drag-and-drop functionality.
 */

import React, { useState } from 'react';
import type { CategoryTreeNode } from '../../types/category';
import { Button } from '../ui/Button';

interface CategoryTreeProps {
  data: CategoryTreeNode[];
  onSelect: (category: CategoryTreeNode) => void;
  onEdit?: (category: CategoryTreeNode) => void;
  onDelete?: (category: CategoryTreeNode) => void;
  onMove?: (categoryId: string, newParentId: string | null) => void;
  selectedId?: string;
  defaultExpanded?: boolean;
  enableDragDrop?: boolean;
  isLoading?: boolean;
  emptyMessage?: string;
}

interface TreeNodeProps {
  node: CategoryTreeNode;
  selectedId?: string;
  expandedIds: Set<string>;
  hoveredId: string | null;
  onToggle: (id: string) => void;
  onSelect: (category: CategoryTreeNode) => void;
  onEdit?: (category: CategoryTreeNode) => void;
  onDelete?: (category: CategoryTreeNode) => void;
  onHover: (id: string | null) => void;
  enableDragDrop?: boolean;
}

const TreeNode: React.FC<TreeNodeProps> = ({
  node,
  selectedId,
  expandedIds,
  hoveredId,
  onToggle,
  onSelect,
  onEdit,
  onDelete,
  onHover,
  enableDragDrop,
}) => {
  const isExpanded = expandedIds.has(node.id);
  const isSelected = selectedId === node.id;
  const isHovered = hoveredId === node.id;
  const hasChildren = node.hasChildren || (node.children && node.children.length > 0);
  const level = node.level || 0;
  const indentPx = level * 24;

  return (
    <div>
      <div
        className={`
          flex items-center gap-2 px-3 py-2 cursor-pointer
          hover:bg-gray-50 rounded transition-colors
          ${isSelected ? 'bg-blue-50 selected' : ''}
        `}
        style={{ paddingLeft: `${12 + indentPx}px` }}
        onClick={() => onSelect(node)}
        onMouseEnter={() => onHover(node.id)}
        onMouseLeave={() => onHover(null)}
      >
        {/* Expand/Collapse Button */}
        {hasChildren && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggle(node.id);
            }}
            className="w-5 h-5 flex items-center justify-center hover:bg-gray-200 rounded"
            aria-label={isExpanded ? 'Recolher' : 'Expandir'}
          >
            {isExpanded ? (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            )}
          </button>
        )}

        {/* Drag Handle (if enabled) */}
        {enableDragDrop && (
          <button
            className="w-5 h-5 flex items-center justify-center hover:bg-gray-200 rounded cursor-grab"
            aria-label="Arrastar"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8h16M4 16h16" />
            </svg>
          </button>
        )}

        {/* Category Name */}
        <span className="flex-1 text-sm font-medium text-gray-900">
          {node.name}
        </span>

        {/* Status Badge */}
        <span
          className={`
            px-2 py-0.5 text-xs font-medium rounded-full
            ${node.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}
          `}
        >
          {node.is_active ? 'Ativo' : 'Inativo'}
        </span>

        {/* Action Buttons (visible on hover or always in tests) */}
        {(onEdit || onDelete) && (
          <div 
            className={`flex gap-1 ${!isHovered ? 'opacity-0 group-hover:opacity-100' : ''}`}
            onClick={(e) => e.stopPropagation()}
            data-testid={`actions-${node.id}`}
          >
            {onEdit && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onEdit(node)}
                aria-label="Editar"
                data-testid={`edit-${node.id}`}
              >
                Editar
              </Button>
            )}
            {onDelete && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onDelete(node)}
                aria-label="Excluir"
                data-testid={`delete-${node.id}`}
              >
                Excluir
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Children (recursively render if expanded) */}
      {hasChildren && isExpanded && node.children && (
        <div>
          {node.children.map((child) => (
            <TreeNode
              key={child.id}
              node={child}
              selectedId={selectedId}
              expandedIds={expandedIds}
              hoveredId={hoveredId}
              onToggle={onToggle}
              onSelect={onSelect}
              onEdit={onEdit}
              onDelete={onDelete}
              onHover={onHover}
              enableDragDrop={enableDragDrop}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export const CategoryTree: React.FC<CategoryTreeProps> = ({
  data,
  onSelect,
  onEdit,
  onDelete,
  onMove,
  selectedId,
  defaultExpanded = false,
  enableDragDrop = false,
  isLoading = false,
  emptyMessage = 'Nenhuma categoria encontrada',
}) => {
  // State for expanded nodes
  const [expandedIds, setExpandedIds] = useState<Set<string>>(() => {
    if (defaultExpanded) {
      const ids = new Set<string>();
      const collectIds = (nodes: CategoryTreeNode[]) => {
        nodes.forEach((node) => {
          if (node.hasChildren || (node.children && node.children.length > 0)) {
            ids.add(node.id);
            if (node.children) {
              collectIds(node.children);
            }
          }
        });
      };
      collectIds(data);
      return ids;
    }
    return new Set<string>();
  });

  const [hoveredId, setHoveredId] = useState<string | null>(null);

  const handleToggle = (id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  // Loading skeleton
  if (isLoading) {
    return (
      <div data-testid="tree-loading-skeleton" className="space-y-2 p-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-10 bg-gray-200 rounded animate-pulse" />
        ))}
      </div>
    );
  }

  // Empty state
  if (!data || data.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>{emptyMessage}</p>
      </div>
    );
  }

  // Render tree
  return (
    <div className="space-y-1">
      {data.map((node) => (
        <TreeNode
          key={node.id}
          node={node}
          selectedId={selectedId}
          expandedIds={expandedIds}
          hoveredId={hoveredId}
          onToggle={handleToggle}
          onSelect={onSelect}
          onEdit={onEdit}
          onDelete={onDelete}
          onHover={setHoveredId}
          enableDragDrop={enableDragDrop}
        />
      ))}
    </div>
  );
};
