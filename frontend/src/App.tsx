import { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="max-w-4xl w-full space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-foreground">
            Sistema de Gerenciamento de Estoque
          </h1>
          <p className="text-xl text-muted-foreground">
            White Label Multi-tenant Inventory Management System
          </p>
        </div>

        <div className="bg-card border border-border rounded-lg p-8 shadow-sm">
          <div className="text-center space-y-6">
            <div className="space-y-2">
              <h2 className="text-2xl font-semibold">Setup Completo! 🎉</h2>
              <p className="text-muted-foreground">
                Frontend React + TypeScript + Vite está funcionando
              </p>
            </div>

            <div className="space-y-4">
              <div className="p-6 bg-secondary rounded-md">
                <p className="text-sm text-secondary-foreground mb-2">Counter de Teste:</p>
                <button
                  onClick={() => setCount((count) => count + 1)}
                  className="px-6 py-3 bg-primary text-primary-foreground rounded-md hover:opacity-90 transition-opacity font-medium"
                >
                  Count is {count}
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
                <div className="p-4 border border-border rounded-md">
                  <h3 className="font-semibold text-sm mb-1">✅ React 18</h3>
                  <p className="text-xs text-muted-foreground">Component rendering</p>
                </div>
                <div className="p-4 border border-border rounded-md">
                  <h3 className="font-semibold text-sm mb-1">✅ TypeScript</h3>
                  <p className="text-xs text-muted-foreground">Type safety enabled</p>
                </div>
                <div className="p-4 border border-border rounded-md">
                  <h3 className="font-semibold text-sm mb-1">✅ TailwindCSS</h3>
                  <p className="text-xs text-muted-foreground">Styling working</p>
                </div>
              </div>
            </div>

            <div className="pt-4">
              <p className="text-sm text-muted-foreground">
                Próximo passo: Implementar Phase 2 (Database + Auth + Models)
              </p>
            </div>
          </div>
        </div>

        <div className="text-center">
          <p className="text-xs text-muted-foreground">
            Branch: 001-sistema-de-gerenciamento | Phase 1: Setup ✅ Complete
          </p>
        </div>
      </div>
    </div>
  )
}

export default App
