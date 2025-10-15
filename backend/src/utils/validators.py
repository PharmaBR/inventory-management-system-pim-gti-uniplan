"""
Validation utilities for business logic.

Provides SKU validation, normalization, and generation functions.
Used by ProductService to enforce business rules.

Task: T065 - SKU validation helpers
"""

import re
from typing import Optional, List
from uuid import UUID


def normalize_sku(sku: str) -> str:
    """
    Normalize SKU to uppercase and trim whitespace.
    
    Args:
        sku: Raw SKU string
        
    Returns:
        Normalized SKU (uppercase, trimmed)
        
    Raises:
        ValueError: If SKU is empty after normalization
    """
    if not sku:
        raise ValueError("SKU cannot be empty")
    
    normalized = sku.strip().upper()
    
    if not normalized:
        raise ValueError("SKU cannot be empty or whitespace only")
    
    return normalized


def validate_sku_format(sku: str) -> None:
    """
    Validate SKU format and constraints.
    
    Rules:
    - Length: 3-100 characters
    - Characters: alphanumeric, hyphens, underscores, periods only
    - Must not be empty
    
    Args:
        sku: SKU to validate
        
    Raises:
        ValueError: If SKU format is invalid
    """
    if not sku or not sku.strip():
        raise ValueError("SKU cannot be empty")
    
    # Length validation
    if len(sku) < 3:
        raise ValueError("SKU must be at least 3 characters long")
    
    if len(sku) > 100:
        raise ValueError("SKU must not exceed 100 characters")
    
    # Character validation (alphanumeric + -, _, .)
    if not re.match(r'^[A-Z0-9\-_.]+$', sku):
        raise ValueError(
            "SKU can only contain alphanumeric characters, hyphens, underscores, and periods"
        )


async def validate_sku_unique(
    sku: str,
    tenant_id: UUID,
    existing_product: Optional[dict] = None,
    current_product_id: Optional[UUID] = None,
) -> None:
    """
    Validate that SKU is unique within tenant.
    
    Args:
        sku: SKU to validate
        tenant_id: Tenant UUID
        existing_product: Dict with existing product data (if found)
        current_product_id: UUID of product being updated (for updates)
        
    Raises:
        ValueError: If SKU already exists in tenant
    """
    if not existing_product:
        return  # No conflict
    
    # If updating the same product, allow keeping the same SKU
    if current_product_id and existing_product.get("id") == current_product_id:
        return
    
    # Different product with same SKU in same tenant
    if existing_product.get("tenant_id") == tenant_id:
        raise ValueError(f"SKU '{sku}' already exists in this tenant")


async def validate_sku(
    sku: str,
    tenant_id: UUID,
    existing_product: Optional[dict] = None,
    current_product_id: Optional[UUID] = None,
) -> str:
    """
    Complete SKU validation pipeline.
    
    Combines normalization, format validation, and uniqueness check.
    
    Args:
        sku: Raw SKU string
        tenant_id: Tenant UUID
        existing_product: Existing product with same SKU (if any)
        current_product_id: ID of product being updated
        
    Returns:
        Normalized, validated SKU
        
    Raises:
        ValueError: If validation fails
    """
    # Normalize
    normalized_sku = normalize_sku(sku)
    
    # Validate format
    validate_sku_format(normalized_sku)
    
    # Validate uniqueness
    await validate_sku_unique(
        normalized_sku,
        tenant_id,
        existing_product,
        current_product_id,
    )
    
    return normalized_sku


def suggest_sku_format() -> List[str]:
    """
    Suggest SKU format patterns.
    
    Returns:
        List of recommended SKU format examples
    """
    return [
        "PREFIX-CATEGORY-001",
        "BRAND-PRODUCT-SKU",
        "DEPT-ITEM-NUM",
        "ABC-123-XYZ",
    ]


async def generate_sku(
    product_name: str,
    tenant_id: UUID,
    existing_skus: Optional[List[str]] = None,
) -> str:
    """
    Auto-generate SKU from product name.
    
    Creates SKU by:
    1. Taking first letters of words in product name
    2. Adding numeric suffix if needed to avoid duplicates
    
    Args:
        product_name: Product name to generate SKU from
        tenant_id: Tenant UUID
        existing_skus: List of existing SKUs to avoid duplicates
        
    Returns:
        Generated SKU
    """
    # Extract first letters of words
    words = product_name.upper().split()
    if len(words) >= 2:
        base = "".join([word[0] for word in words[:3]])  # Max 3 letters
    else:
        base = product_name[:6].upper()  # First 6 chars
    
    # Remove non-alphanumeric
    base = re.sub(r'[^A-Z0-9]', '', base)
    
    if not base:
        base = "PROD"
    
    # Check for duplicates
    existing_skus = existing_skus or []
    
    if base not in existing_skus:
        return base
    
    # Add numeric suffix
    for i in range(1, 1000):
        candidate = f"{base}-{i:03d}"
        if candidate not in existing_skus:
            return candidate
    
    # Fallback
    import random
    return f"{base}-{random.randint(1000, 9999)}"
