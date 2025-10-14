import React from 'react';
import { useTranslation } from 'react-i18next';

interface HeaderProps {
  tenantName?: string;
  userName?: string;
  onLogout?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ tenantName, userName, onLogout }) => {
  const { t, i18n } = useTranslation();
  
  const toggleLanguage = () => {
    const newLang = i18n.language === 'pt-BR' ? 'en-US' : 'pt-BR';
    i18n.changeLanguage(newLang);
  };
  
  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div className="flex items-center justify-between px-6 py-4">
        {/* Logo / Tenant */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
          <div>
            <h1 className="text-lg font-semibold text-gray-900">
              {tenantName || t('common.app_name')}
            </h1>
          </div>
        </div>
        
        {/* Actions */}
        <div className="flex items-center gap-4">
          {/* Language Toggle */}
          <button
            onClick={toggleLanguage}
            className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
          >
            {i18n.language === 'pt-BR' ? '🇧🇷 PT' : '🇺🇸 EN'}
          </button>
          
          {/* User Menu */}
          {userName && (
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-700">{userName}</span>
              <button
                onClick={onLogout}
                className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
              >
                {t('auth.logout')}
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
