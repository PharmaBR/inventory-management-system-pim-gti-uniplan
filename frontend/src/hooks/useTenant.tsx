import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { tenantAPI } from '../services/api';

interface Tenant {
  id: string;
  name: string;
  slug: string;
  logo_url?: string;
  primary_color: string;
  secondary_color: string;
  max_users: number;
  max_products: number;
  max_storage_mb: number;
  settings: Record<string, any>;
  is_active: boolean;
}

interface TenantContextType {
  tenant: Tenant | null;
  isLoading: boolean;
  refetchTenant: () => Promise<void>;
}

const TenantContext = createContext<TenantContextType | undefined>(undefined);

export const TenantProvider = ({ children }: { children: ReactNode }) => {
  const [tenant, setTenant] = useState<Tenant | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  const fetchTenant = async () => {
    try {
      setIsLoading(true);
      const response = await tenantAPI.getCurrent();
      setTenant(response.data);
      
      // Store tenant slug for API requests
      localStorage.setItem('tenant_slug', response.data.slug);
      
      // Apply tenant branding
      if (response.data.primary_color) {
        document.documentElement.style.setProperty('--color-primary', response.data.primary_color);
      }
      if (response.data.secondary_color) {
        document.documentElement.style.setProperty('--color-secondary', response.data.secondary_color);
      }
    } catch (error) {
      console.error('Failed to fetch tenant:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  useEffect(() => {
    // Extract tenant slug from subdomain
    const hostname = window.location.hostname;
    const parts = hostname.split('.');
    
    // If subdomain exists (e.g., tenant1.example.com)
    if (parts.length > 2) {
      const slug = parts[0];
      localStorage.setItem('tenant_slug', slug);
    }
    
    fetchTenant();
  }, []);
  
  const value: TenantContextType = {
    tenant,
    isLoading,
    refetchTenant: fetchTenant,
  };
  
  return <TenantContext.Provider value={value}>{children}</TenantContext.Provider>;
};

export const useTenant = () => {
  const context = useContext(TenantContext);
  if (!context) {
    throw new Error('useTenant must be used within TenantProvider');
  }
  return context;
};
