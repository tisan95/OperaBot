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
  const { isAuthenticated, isLoading } = useAuthContext();
  const router = useRouter();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
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
