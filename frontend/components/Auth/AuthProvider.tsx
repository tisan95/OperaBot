"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { AuthContextType, User, Company } from "@/lib/types";
import { apiFetch } from "@/lib/api";

export const AuthContext = createContext<AuthContextType | undefined>(
  undefined
);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [company, setCompany] = useState<Company | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is already authenticated on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await apiFetch("/auth/me");
      if (response && response.user) {
        setUser(response.user);
        setCompany(response.company);
      }
    } catch (error) {
      // Not authenticated
      setUser(null);
      setCompany(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (
    email: string,
    password: string,
    company_name: string
  ) => {
    const response = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password, company_name }),
    });

    if (response && response.user) {
      setUser(response.user);
      setCompany(response.company);
    } else {
      throw new Error(response.detail || "Login failed");
    }
  };

  const register = async (
    email: string,
    password: string,
    company_name: string
  ) => {
    const response = await apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, company_name }),
    });

    if (response && response.user) {
      setUser(response.user);
      setCompany(response.company);
    } else {
      throw new Error(response.detail || "Registration failed");
    }
  };

  const logout = async () => {
    try {
      await apiFetch("/auth/logout", { method: "POST" });
    } finally {
      setUser(null);
      setCompany(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        company,
        isLoading,
        login,
        register,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuthContext = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuthContext must be used within AuthProvider");
  }
  return context;
};
