# Phase 5 Session 1: Category Management UI - Contract Tests

**Date**: 2025-10-15  
**Branch**: `001-sistema-de-gerenciamento`  
**Objective**: Define contract tests for Category Management UI components

## 📊 Current State

### Backend Status ✅
- **Categories API**: Complete with 81.12% coverage
- **Endpoints Available**:
  - `GET /api/v1/categories` - List with filters
  - `GET /api/v1/categories/{id}` - Get by ID
  - `POST /api/v1/categories` - Create
  - `PUT /api/v1/categories/{id}` - Update
  - `DELETE /api/v1/categories/{id}` - Delete
  - Hierarchical support with parent_id
  - Validation for circular references
  - Cascade delete to root

### Frontend Status
- **Stack**: React 18 + TypeScript + Vite + TailwindCSS
- **State Management**: Zustand + React Query
- **UI Components**: Button, Input, Modal, Toast (ready)
- **API Client**: Axios with interceptors configured
- **Pages**: Empty (only placeholder App.tsx)

---

## 🎯 Session 1 Goals

Create **contract tests** that define expected behavior for:

1. **Category API Service** - Frontend client for backend API
2. **Category Types** - TypeScript interfaces matching backend schemas
3. **CategoryTree Component** - Hierarchical tree with drag-and-drop
4. **CategoryForm Component** - Create/edit modal form
5. **CategoryList Component** - Filterable list view
6. **CategorySelector Component** - Dropdown for product forms
7. **CategoriesPage** - Main management page
8. **useCategories Hook** - React Query integration

---

## 📝 Contract Tests to Create

### 1. Category API Service (`tests/unit/services/categories.test.ts`)

**File**: `src/services/categories.ts`

#### Tests (10 total):

1. **getCategoriesList()**
   - ✅ Should call GET /categories with default params
   - ✅ Should apply filters (name, status, parent_id, root_only)
   - ✅ Should handle pagination (skip, limit)
   - ✅ Should include auth token and tenant header

2. **getCategoryById()**
   - ✅ Should call GET /categories/{id}
   - ✅ Should handle 404 errors

3. **createCategory()**
   - ✅ Should call POST /categories with correct data
   - ✅ Should handle validation errors (409 conflict)

4. **updateCategory()**
   - ✅ Should call PUT /categories/{id} with partial data

5. **deleteCategory()**
   - ✅ Should call DELETE /categories/{id}
   - ✅ Should handle 400 errors (products exist)

---

### 2. Category Types (`tests/unit/types/category.test.ts`)

**File**: `src/types/category.ts`

#### Interfaces to Define (5 total):

1. **Category** - Main interface matching CategoryResponse
   ```typescript
   interface Category {
     id: string;
     name: string;
     description?: string;
     parent_id?: string;
     is_active: boolean;
     created_at: string;
     updated_at: string;
   }
   ```

2. **CategoryCreate** - Create payload
   ```typescript
   interface CategoryCreate {
     name: string;
     description?: string;
     parent_id?: string;
   }
   ```

3. **CategoryUpdate** - Update payload (partial)
   ```typescript
   interface CategoryUpdate {
     name?: string;
     description?: string;
     parent_id?: string;
     is_active?: boolean;
   }
   ```

4. **CategoryFilter** - List filters
   ```typescript
   interface CategoryFilter {
     name?: string;
     status?: 'active' | 'inactive';
     parent_id?: string;
     root_only?: boolean;
     skip?: number;
     limit?: number;
   }
   ```

5. **CategoryTreeNode** - Tree structure
   ```typescript
   interface CategoryTreeNode extends Category {
     children: CategoryTreeNode[];
     level: number;
   }
   ```

**Tests**: Type validation and proper TypeScript inference

---

### 3. CategoryTree Component (`tests/unit/components/CategoryTree.test.tsx`)

**File**: `src/components/categories/CategoryTree.tsx`

#### Tests (12 total):

1. **Rendering**
   - ✅ Should render empty state when no categories
   - ✅ Should render flat list when all root categories
   - ✅ Should render hierarchical tree with indentation
   - ✅ Should show expand/collapse icons for parent nodes

2. **Interaction**
   - ✅ Should expand/collapse categories on click
   - ✅ Should select category on click
   - ✅ Should highlight selected category

3. **Drag and Drop**
   - ✅ Should allow dragging categories
   - ✅ Should show drop indicator on valid targets
   - ✅ Should prevent dropping on own children (circular)
   - ✅ Should call onMove callback with correct IDs
   - ✅ Should show loading state during move operation

---

### 4. CategoryForm Component (`tests/unit/components/CategoryForm.test.tsx`)

**File**: `src/components/categories/CategoryForm.tsx`

#### Tests (10 total):

1. **Create Mode**
   - ✅ Should render empty form for create
   - ✅ Should have "Criar Categoria" title
   - ✅ Should show parent selector (optional)
   - ✅ Should validate required fields (name)
   - ✅ Should call onCreate on submit

2. **Edit Mode**
   - ✅ Should pre-populate form with category data
   - ✅ Should have "Editar Categoria" title
   - ✅ Should disable parent selector if has children
   - ✅ Should call onUpdate on submit

3. **Validation**
   - ✅ Should show error for empty name
   - ✅ Should trim whitespace from name

---

### 5. CategoryList Component (`tests/unit/components/CategoryList.test.tsx`)

**File**: `src/components/categories/CategoryList.tsx`

#### Tests (8 total):

1. **Rendering**
   - ✅ Should render categories in table format
   - ✅ Should show category name, description, status
   - ✅ Should show parent category name (if exists)
   - ✅ Should show action buttons (edit, delete)

2. **Filtering**
   - ✅ Should filter by name (search input)
   - ✅ Should filter by status (active/inactive toggle)
   - ✅ Should filter by parent (show only root checkbox)

3. **Actions**
   - ✅ Should call onEdit when edit button clicked
   - ✅ Should show confirmation modal on delete
   - ✅ Should call onDelete after confirmation

---

### 6. CategorySelector Component (`tests/unit/components/CategorySelector.test.tsx`)

**File**: `src/components/categories/CategorySelector.tsx`

#### Tests (6 total):

1. **Rendering**
   - ✅ Should render as dropdown/select
   - ✅ Should show hierarchical structure with indentation
   - ✅ Should show "Nenhuma" option for root level
   - ✅ Should pre-select current value

2. **Interaction**
   - ✅ Should call onChange when selection changes
   - ✅ Should filter out category and its children (when editing)

---

### 7. CategoriesPage (`tests/unit/pages/CategoriesPage.test.tsx`)

**File**: `src/pages/CategoriesPage.tsx`

#### Tests (8 total):

1. **Layout**
   - ✅ Should render page header with "Categorias" title
   - ✅ Should show "Nova Categoria" button
   - ✅ Should toggle between Tree and List views

2. **Loading States**
   - ✅ Should show skeleton loader while fetching
   - ✅ Should show error message on fetch failure

3. **CRUD Operations**
   - ✅ Should open create form on "Nova Categoria" click
   - ✅ Should open edit form on category edit click
   - ✅ Should refresh list after create/update/delete
   - ✅ Should show toast notifications for success/error

---

### 8. useCategories Hook (`tests/unit/hooks/useCategories.test.ts`)

**File**: `src/hooks/useCategories.ts`

#### Tests (10 total):

1. **Query Hooks**
   - ✅ Should fetch categories list with useCategories()
   - ✅ Should fetch single category with useCategory(id)
   - ✅ Should apply filters to query key
   - ✅ Should cache results properly

2. **Mutation Hooks**
   - ✅ Should create category with useCreateCategory()
   - ✅ Should update category with useUpdateCategory()
   - ✅ Should delete category with useDeleteCategory()
   - ✅ Should invalidate queries after mutations

3. **Optimistic Updates**
   - ✅ Should optimistically update list on create
   - ✅ Should rollback on error

---

## 📊 Summary

### Test Count: **64 Contract Tests**

| Component | Tests |
|-----------|-------|
| Category API Service | 10 |
| Category Types | (Type definitions) |
| CategoryTree | 12 |
| CategoryForm | 10 |
| CategoryList | 8 |
| CategorySelector | 6 |
| CategoriesPage | 8 |
| useCategories Hook | 10 |
| **TOTAL** | **64** |

---

## 🎯 Success Criteria

1. ✅ All 64 contract tests defined and **failing** (RED)
2. ✅ Clear test descriptions defining expected behavior
3. ✅ Proper test structure with arrange-act-assert
4. ✅ Mocks for API calls and React Query
5. ✅ Ready for Session 2 implementation (GREEN phase)

---

## 📦 Dependencies Needed

Already installed in `package.json`:
- ✅ `vitest` - Test runner
- ✅ `@testing-library/react` - Component testing
- ✅ `@testing-library/jest-dom` - DOM matchers
- ✅ `@tanstack/react-query` - Data fetching

May need to add:
- `@testing-library/user-event` - User interaction simulation
- `@dnd-kit/core` - Drag and drop (for CategoryTree)
- `@dnd-kit/sortable` - Sortable lists

---

## 🚀 Next Steps

1. Create test file structure
2. Write all 64 contract tests
3. Run tests (expect all RED)
4. Verify test quality and coverage
5. Move to Session 2: Implementation

---

## 📝 Notes

- Following same TDD methodology from Phase 3 & 4
- Contract tests define "what" not "how"
- Focus on user-facing behavior, not implementation details
- Use React Testing Library best practices (queries, user events)
- Mock external dependencies (API, React Query)

