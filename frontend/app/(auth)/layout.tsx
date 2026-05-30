"use client";

import { useAuthContext } from "@/components/Auth/AuthProvider";
import Header from "@/components/Shared/Header";
import LoadingSpinner from "@/components/Shared/LoadingSpinner";
import Sidebar from "@/components/Shared/Sidebar";
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
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (user?.status === "pending") {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 px-6 text-center">
        <div className="max-w-md rounded-3xl border border-slate-200 bg-white p-10 shadow-lg">
          <h1 className="text-3xl font-semibold text-slate-900 mb-4">Cuenta pendiente</h1>
          <p className="text-slate-600 leading-7">
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
    <div className="min-h-screen bg-slate-50">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 px-6 py-8">
          {children}
        </main>
      </div>
    </div>
  );
}