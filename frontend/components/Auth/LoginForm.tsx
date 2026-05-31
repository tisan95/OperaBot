"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthContext } from "@/components/Auth/AuthProvider";

interface LoginFormProps {
  onSuccess?: () => void;
}

export default function LoginForm({ onSuccess }: LoginFormProps) {
  const router = useRouter();
  const { login } = useAuthContext();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(email, password, companyName);
      onSuccess?.();
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div
          className="px-4 py-3 rounded-lg text-sm border"
          style={{
            backgroundColor: "rgba(229,62,62,0.08)",
            borderColor: "rgba(229,62,62,0.3)",
            color: "#E53E3E",
          }}
        >
          {error}
        </div>
      )}

      <div>
        <label className="block text-xs font-medium mb-1.5" style={{ color: "#888888" }}>
          Company Name
        </label>
        <input
          type="text"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          required
          className="input"
          placeholder="Your company name"
          disabled={loading}
        />
      </div>

      <div>
        <label className="block text-xs font-medium mb-1.5" style={{ color: "#888888" }}>
          Email
        </label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="input"
          placeholder="you@example.com"
          disabled={loading}
        />
      </div>

      <div>
        <label className="block text-xs font-medium mb-1.5" style={{ color: "#888888" }}>
          Password
        </label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="input"
          placeholder="••••••••"
          disabled={loading}
        />
      </div>

      <button type="submit" disabled={loading} className="btn btn-primary w-full mt-2">
        {loading ? "Logging in..." : "Login"}
      </button>
    </form>
  );
}
