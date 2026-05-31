"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthContext } from "@/components/Auth/AuthProvider";

export default function RegisterForm() {
  const router = useRouter();
  const { register } = useAuthContext();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);

    try {
      await register(email, password, companyName);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Registration failed. Please try again.");
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
          minLength={8}
          className="input"
          placeholder="••••••••"
          disabled={loading}
        />
        <p className="text-xs mt-1" style={{ color: "#555555" }}>Minimum 8 characters</p>
      </div>

      <div>
        <label className="block text-xs font-medium mb-1.5" style={{ color: "#888888" }}>
          Confirm Password
        </label>
        <input
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
          className="input"
          placeholder="••••••••"
          disabled={loading}
        />
      </div>

      <button type="submit" disabled={loading} className="btn btn-primary w-full mt-2">
        {loading ? "Creating account..." : "Create Account"}
      </button>
    </form>
  );
}
