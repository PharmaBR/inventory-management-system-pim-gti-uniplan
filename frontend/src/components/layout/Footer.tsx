import React from 'react';

export const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <p>
            © {currentYear} Inventory Management System - PIM GTI UNIPLAN
          </p>
          <div className="flex items-center gap-4">
            <a href="#" className="hover:text-gray-900 transition-colors">
              Ajuda
            </a>
            <a href="#" className="hover:text-gray-900 transition-colors">
              Privacidade
            </a>
            <a href="#" className="hover:text-gray-900 transition-colors">
              Termos
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};
