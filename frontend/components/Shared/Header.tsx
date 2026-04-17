"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { useAuthContext } from "@/components/Auth/AuthProvider";

export default function Header() {
  const router = useRouter();
  const { user, company, logout, isAuthenticated } = useAuthContext();

  const handleLogout = async () => {
    await logout();
    router.push("/");
  };

  if (!isAuthenticated) return null;

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex justify-between items-center">
          {/* Logo & Company */}
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0">
              <span className="text-2xl font-bold text-indigo-600">OperaBot</span>
            </div>
            {company && (
              <div className="hidden sm:block pl-4 border-l border-slate-200">
                <p className="text-sm font-medium text-slate-900">{company.name}</p>
                <p className="text-xs text-slate-500 mt-0.5">Operational Knowledge Assistant</p>
              </div>
            )}
          </div>

          {/* User Info & Logout */}
          <div className="flex items-center space-x-6">
            {user && (
              <div className="hidden sm:block text-right">
                <p className="text-sm font-medium text-slate-900">{user.email}</p>
                <p className="text-xs text-slate-500 mt-0.5 capitalize">{user.role}</p>
              </div>
            )}
            <button
              onClick={handleLogout}
              className="btn btn-danger btn-sm"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
