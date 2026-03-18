import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertOctagon, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-6 text-center font-sans">
          <div className="max-w-md w-full bg-zinc-900 border border-white/10 p-8 rounded-2xl shadow-2xl">
            <div className="w-16 h-16 bg-rose-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
              <AlertOctagon className="w-8 h-8 text-rose-500" />
            </div>
            <h1 className="text-xl font-bold text-white mb-2">Something went wrong</h1>
            <p className="text-zinc-400 text-sm mb-8 leading-relaxed">
              An unexpected error occurred in the interface. We've been notified and are working on it.
            </p>
            
            <div className="bg-black/20 rounded-lg p-4 mb-8 text-left overflow-auto max-h-32 border border-white/5">
              <code className="text-xs text-rose-400/80 font-mono break-all">
                {this.state.error?.toString()}
              </code>
            </div>

            <button
              onClick={this.handleReset}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-white text-black font-bold rounded-xl hover:bg-zinc-200 transition-all shadow-[0_0_20px_rgba(255,255,255,0.1)]"
            >
              <RefreshCw className="w-4 h-4" />
              Reload Application
            </button>
          </div>
        </div>
      );
    }

    return this.children;
  }
}
