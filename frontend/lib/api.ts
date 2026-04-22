"use client";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const apiFetch = async (
  endpoint: string,
  options?: RequestInit
): Promise<any> => {
  const url = `${API_URL}${endpoint}`;

  // Solo agrega Content-Type si no es FormData
  // FormData requiere que el navegador establezca multipart/form-data automáticamente
  const isFormData = options?.body instanceof FormData;
  const headers: Record<string, string> = !isFormData
    ? { "Content-Type": "application/json" }
    : {};

  const response = await fetch(url, {
    ...options,
    headers: {
      ...headers,
      ...options?.headers,
    },
    credentials: "include", // Include HTTP-only cookies
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || data.message || "API request failed");
  }

  return data;
};
