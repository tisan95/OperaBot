"use client";

// Token management (for HTTP-only cookies set by backend)
// Frontend just needs to track authentication state

export const getAuthToken = (): string | null => {
  // Token is stored in HTTP-only cookie by backend
  // Frontend cannot access it directly (security feature)
  return null;
};

export const setAuthToken = (token: string): void => {
  // Don't store tokens in localStorage
  // Backend sets HTTP-only cookie automatically
};

export const clearAuthToken = (): void => {
  // Backend clears HTTP-only cookie on logout
};

export const isTokenExpired = (): boolean => {
  // Check if auth state is still valid
  // Relies on backend HTTP-only cookie expiration
  return false;
};
