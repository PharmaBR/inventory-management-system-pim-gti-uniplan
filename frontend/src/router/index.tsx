/**
 * App Router Configuration
 * 
 * Defines all application routes and navigation structure.
 */

import React from 'react';
import { createBrowserRouter, RouterProvider, Outlet, Navigate } from 'react-router-dom';
import { CategoriesPage } from '../pages/CategoriesPage';
import { LoginPage } from '../pages/auth/LoginPage';
import { ErrorBoundary } from '../components/ErrorBoundary';
import { ProtectedRoute } from '../components/ProtectedRoute';
import { useAuth } from '../hooks/useAuth';

// Layout component with navigation
const Layout: React.FC = () => {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
      window.location.href = '/login';
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-8">
              <h1 className="text-xl font-bold text-gray-900">
                Sistema de Gestão
              </h1>
              <div className="flex gap-4">
                <a
                  href="/categories"
                  className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                >
                  Categorias
                </a>
                <a
                  href="/products"
                  className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                >
                  Produtos
                </a>
              </div>
            </div>
            
            {/* User Menu */}
            <div className="flex items-center gap-4">
              {user && (
                <>
                  <span className="text-sm text-gray-600">
                    {user.name || user.email}
                  </span>
                  <button
                    onClick={handleLogout}
                    className="px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-md transition-colors"
                  >
                    Sair
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto">
        <ErrorBoundary>
          <Outlet />
        </ErrorBoundary>
      </main>
    </div>
  );
};

// Home page placeholder
const HomePage: React.FC = () => {
  return (
    <div className="py-12 text-center">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">
        Bem-vindo ao Sistema de Gestão
      </h2>
      <p className="text-gray-600 mb-8">
        Escolha uma seção para começar
      </p>
      <div className="flex gap-4 justify-center">
        <a
          href="/categories"
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Gerenciar Categorias
        </a>
        <a
          href="/products"
          className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
        >
          Gerenciar Produtos
        </a>
      </div>
    </div>
  );
};

// Products page placeholder
const ProductsPage: React.FC = () => {
  return (
    <div className="py-12 text-center">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">
        Produtos
      </h2>
      <p className="text-gray-600">
        Página de produtos em desenvolvimento...
      </p>
    </div>
  );
};

// 404 page
const NotFoundPage: React.FC = () => {
  return (
    <div className="py-12 text-center">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">
        404 - Página não encontrada
      </h2>
      <p className="text-gray-600 mb-8">
        A página que você está procurando não existe.
      </p>
      <a
        href="/"
        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors inline-block"
      >
        Voltar para Home
      </a>
    </div>
  );
};

// Router configuration
export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <Layout />
      </ProtectedRoute>
    ),
    errorElement: <ErrorBoundary />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: 'categories',
        element: <CategoriesPage />,
      },
      {
        path: 'products',
        element: <ProductsPage />,
      },
      {
        path: '*',
        element: <NotFoundPage />,
      },
    ],
  },
]);

// Router Provider Component
export const AppRouter: React.FC = () => {
  return <RouterProvider router={router} />;
};
