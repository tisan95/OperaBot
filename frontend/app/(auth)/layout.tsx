"use client";

import { useAuthContext } from "@/components/Auth/AuthProvider";
import ErrorBoundary from "@/components/Shared/ErrorBoundary";
import Header from "@/components/Shared/Header";
import LoadingSpinner from "@/components/Shared/LoadingSpinner";
import Sidebar from "@/components/Shared/Sidebar";
import { SidebarProvider } from "@/components/Shared/SidebarContext";
import { useRouter } from "next/navigation";
import { ReactNode } from "react";

interface AuthLayoutProps {
  children: ReactNode;
}

export default function AuthLayout({ children }: AuthLayoutProps) {
  const { user, isAuthenticated, isLoading } = useAuthContext();
  const router = useRouter();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg">
        <LoadingSpinner />
      </div>
    );
  }

  if (user?.status === "pending") {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-6 text-center bg-bg">
        <div className="card card-padding max-w-md rounded-2xl">
          <h1 className="text-2xl font-bold mb-3 text-text-primary">Cuenta pendiente</h1>
          <p className="text-sm leading-relaxed text-text-secondary">
            Tu cuenta está pendiente de aprobación por un administrador.
            En cuanto sea aprobada podrás acceder al dashboard.
          </p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    router.push("/");
    return null;
  }

  return (
    <SidebarProvider>
      <ErrorBoundary>
        {/* h-screen + overflow-hidden = shell layout. main scrolls internally. */}
        <div className="h-screen flex flex-col bg-bg overflow-hidden">
          <Header />
          <div className="flex flex-1 min-h-0">
            <Sidebar />
            {/* flex flex-col permite que hijos con flex-1 llenen el espacio (chat) */}
            <main className="flex-1 min-h-0 overflow-y-auto px-6 py-8 flex flex-col">
              {children}
            </main>
          </div>
        </div>
      </ErrorBoundary>
    </SidebarProvider>
  );
}
