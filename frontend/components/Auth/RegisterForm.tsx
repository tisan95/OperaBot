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
      setError("Las contraseñas no coinciden.");
      return;
    }

    setLoading(true);

    try {
      await register(email, password, companyName);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Error al registrarse. Inténtalo de nuevo.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="px-4 py-3 rounded-lg text-sm border bg-error/8 border-error/30 text-error">
          {error}
        </div>
      )}

      <div>
        <label className="block text-xs font-medium mb-1.5 text-text-secondary">
          Nombre de empresa
        </label>
        <input
          type="text"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          required
          className="input"
          placeholder="Tu empresa"
          disabled={loading}
        />
      </div>

      <div>
        <label className="block text-xs font-medium mb-1.5 text-text-secondary">
          Email
        </label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="input"
          placeholder="tu@empresa.com"
          disabled={loading}
        />
      </div>

      <div>
        <label className="block text-xs font-medium mb-1.5 text-text-secondary">
          Contraseña
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
        <p className="text-xs mt-1 text-muted">Mínimo 8 caracteres</p>
      </div>

      <div>
        <label className="block text-xs font-medium mb-1.5 text-text-secondary">
          Confirmar contraseña
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
        {loading ? "Creando cuenta..." : "Crear cuenta"}
      </button>
    </form>
  );
}
