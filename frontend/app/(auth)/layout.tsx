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
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: "#0A0A0A" }}>
        <LoadingSpinner />
      </div>
    );
  }

  if (user?.status === "pending") {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-6 text-center" style={{ backgroundColor: "#0A0A0A" }}>
        <div className="card card-padding max-w-md rounded-2xl">
          <h1 className="text-2xl font-bold mb-3" style={{ color: "#F5F5F5" }}>Cuenta pendiente</h1>
          <p className="text-sm leading-relaxed" style={{ color: "#888888" }}>
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
    <div className="min-h-screen" style={{ backgroundColor: "#0A0A0A" }}>
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
