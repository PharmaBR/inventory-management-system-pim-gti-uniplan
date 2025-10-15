# Phase 4 - Categories CRUD - Session 1: Test Planning

**Date:** 15 de outubro de 2025  
**Status:** ✅ Contract Tests Created  
**Methodology:** TDD (Test-Driven Development)

## Objectives

Create comprehensive test coverage for Categories CRUD following the same successful approach from Phase 3 (Products).

## Contract Tests Created: 23

### CREATE Category (5 tests)
- ✅ `test_create_category_success` - Basic creation
- ✅ `test_create_subcategory_with_parent` - Hierarchical structure
- ✅ `test_create_category_duplicate_name_fails` - Unique constraint
- ✅ `test_create_category_missing_name_fails` - Validation
- ✅ `test_create_category_requires_authentication` - Security

### GET Category by ID (3 tests)
- ✅ `test_get_category_by_id_success` - Retrieve existing
- ✅ `test_get_category_not_found` - 404 handling
- ✅ `test_get_category_from_another_tenant_fails` - Tenant isolation

### LIST Categories (7 tests)
- ✅ `test_list_categories_success` - Basic pagination
- ✅ `test_list_categories_with_pagination` - Page control
- ✅ `test_list_categories_filter_by_name` - Name search
- ✅ `test_list_categories_filter_by_status` - Status filter
- ✅ `test_list_categories_filter_by_parent` - Subcategories
- ✅ `test_list_root_categories_only` - Root level only
- ✅ `test_category_count_metadata` - Accurate counts

### UPDATE Category (4 tests)
- ✅ `test_update_category_success` - Full update
- ✅ `test_update_category_partial_update` - Partial update
- ✅ `test_update_category_duplicate_name_fails` - Unique validation
- ✅ `test_update_category_not_found` - 404 handling

### DELETE Category (4 tests)
- ✅ `test_delete_category_success` - Successful deletion
- ✅ `test_delete_category_not_found` - 404 handling
- ✅ `test_delete_category_with_products_fails` - Foreign key constraint
- ✅ `test_delete_category_cascades_to_children` - SET NULL behavior

## Key Features Specified

### Core CRUD
- ✅ Create categories with optional parent (hierarchical)
- ✅ Retrieve category by ID
- ✅ List with pagination
- ✅ Update category fields
- ✅ Delete with constraints

### Business Rules
- ✅ Unique name per tenant
- ✅ Parent-child relationships (tree structure)
- ✅ Cannot delete if has products
- ✅ Deleting parent makes children root categories
- ✅ Multi-tenant isolation

### Filtering & Search
- ✅ Filter by name (partial match)
- ✅ Filter by status (active/inactive)
- ✅ Filter by parent_id (get subcategories)
- ✅ Filter root categories only (parent_id IS NULL)

### Validation
- ✅ Name is required (max 100 chars)
- ✅ Status defaults to "active"
- ✅ Parent must exist
- ✅ Description is optional

## Data Model Features

```python
class Category:
    id: UUID
    tenant_id: UUID
    name: str  # max 100 chars, unique per tenant
    description: str | None
    parent_id: UUID | None  # self-referential
    status: str  # active/inactive
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    parent: Category | None
    children: List[Category]
    products: List[Product]
```

## Next Steps

### Session 2 - Implementation (Estimated 2-3 hours)
1. Create schemas (`CategoryCreate`, `CategoryUpdate`, `CategoryResponse`)
2. Implement `CategoryService` with:
   - `create()` - validation + unique name check
   - `get()` - by ID with tenant isolation
   - `list()` - filtering, pagination, sorting
   - `update()` - partial update with validation
   - `delete()` - product check + cascade behavior
3. Create API routes (`/api/v1/categories`)
4. Add proper error handling

### Session 3 - Validation (Estimated 1-2 hours)
1. Run contract tests (expect failures)
2. Debug and fix issues
3. Add unit tests for business logic
4. Add integration tests for complex scenarios
5. Target 80%+ coverage

### Session 4 - Coverage & Polish
1. Measure coverage
2. Add missing tests
3. Refine error messages
4. Update documentation
5. Final commit

## Comparison with Phase 3

| Aspect | Phase 3 (Products) | Phase 4 (Categories) |
|--------|-------------------|---------------------|
| Contract Tests | 51 | 23 |
| Complexity | High (SKU generation, filters) | Medium (hierarchy) |
| Special Features | Auto-SKU, 9 filters | Parent-child, cascade |
| Foreign Keys | Category (optional) | Products (constraint) |
| Unique Constraint | SKU per tenant | Name per tenant |

Categories is **simpler** than Products:
- No SKU generation logic
- Fewer filters (4 vs 9)
- Simpler validation rules

**Estimated total effort:** 4-6 hours vs 8-10 hours for Products

## Coverage Target

Following constitution: **80% minimum**

Expected coverage distribution:
- CategoryService: 95%+
- Category routes: 70%+
- Category schemas: 90%+

## Git Workflow

```bash
# Session 1 (Current)
git commit -m "test(categories): create 23 contract tests for Phase 4"

# Session 2
git commit -m "feat(categories): implement CRUD with service and routes"

# Session 3
git commit -m "fix(categories): resolve bugs from TDD validation"
git commit -m "test(categories): add unit and integration tests"

# Session 4
git commit -m "test(categories): achieve 80%+ coverage"
git commit -m "docs(categories): Phase 4 completion report"
```

## Success Criteria

- [ ] All 23 contract tests passing
- [ ] 80%+ code coverage
- [ ] Zero bugs in production logic
- [ ] Proper tenant isolation
- [ ] Hierarchical structure working
- [ ] Product constraint enforced
- [ ] Clean, documented code

---

**Session 1 Complete** ✅  
**Ready for Session 2: Implementation**

Next: Implement `CategoryService`, schemas, and API routes.
