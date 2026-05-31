"use client";

import React from "react";
import { RefreshCw } from "lucide-react";

interface State {
  hasError: boolean;
}

export default class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  State
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error("[ErrorBoundary]", error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          className="min-h-screen flex items-center justify-center px-4"
          style={{ backgroundColor: "#0A0A0A" }}
        >
          <div
            className="card card-padding max-w-md w-full text-center space-y-5"
          >
            <h2 className="text-xl font-bold" style={{ color: "#F5F5F5" }}>
              Algo fue mal
            </h2>
            <p className="text-sm" style={{ color: "#888888" }}>
              Se produjo un error inesperado. Recarga la página para continuar.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="btn btn-primary mx-auto"
            >
              <RefreshCw size={14} strokeWidth={2} />
              Recargar página
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
