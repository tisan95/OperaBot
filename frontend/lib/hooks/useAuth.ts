"use client";

import { useContext } from "react";
import { AuthContext } from "@/components/Auth/AuthProvider";
import { AuthContextType } from "@/lib/types";

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};
