/**
 * Login Page Component
 */

import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

export const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, loginError, isLoggingIn } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    console.log('🔐 Attempting login with:', email);
    
    try {
      const result = await login({ email, password });
      console.log('✅ Login successful:', result);
      
      // On success, navigate to categories
      console.log('🚀 Navigating to /categories');
      navigate('/categories');
    } catch (error) {
      // Error is handled by useAuth hook
      console.error('❌ Login failed:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        {/* Logo/Title */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Sistema de Estoque</h1>
          <p className="text-gray-600 mt-2">Faça login para continuar</p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Email Field */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              E-mail
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="seu@email.com"
              disabled={isLoggingIn}
            />
          </div>

          {/* Password Field */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Senha
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="••••••••"
              disabled={isLoggingIn}
            />
          </div>

          {/* Error Message */}
          {loginError && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
              <strong>Erro:</strong> {loginError.message || 'Credenciais inválidas'}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoggingIn}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoggingIn ? 'Entrando...' : 'Entrar'}
          </button>
        </form>

        {/* Demo Credentials */}
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-xs text-blue-800 font-semibold mb-2">Credenciais de Teste:</p>
          <p className="text-xs text-blue-700">E-mail: admin@example.com</p>
          <p className="text-xs text-blue-700">Senha: admin123</p>
        </div>
      </div>
    </div>
  );
};
