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
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">OperaBot</h1>
          {company && (
            <p className="text-sm text-gray-600">{company.name}</p>
          )}
        </div>

        <div className="flex items-center space-x-4">
          {user && (
            <div className="text-sm">
              <p className="font-medium text-gray-900">{user.email}</p>
              <p className="text-gray-600 capitalize">{user.role}</p>
            </div>
          )}

          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
