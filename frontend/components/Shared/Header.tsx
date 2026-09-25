"use client";

import { useAuthContext } from "@/components/Auth/AuthProvider";
import { useRouter } from "next/navigation";
import { LogOut } from "lucide-react";

const ROLE_LABEL: Record<string, string> = {
  super_admin: "Super Admin",
  admin:       "Admin",
  user:        "User",
};

export default function Header() {
  const router = useRouter();
  const { user, company, logout, isAuthenticated } = useAuthContext();

  const handleLogout = async () => {
    await logout();
    router.push("/");
  };

  if (!isAuthenticated) return null;

  const initial = user?.email?.[0]?.toUpperCase() ?? "U";

  return (
    <header className="sticky top-0 z-40 border-b bg-surface border-border">
      <div className="px-6 h-14 flex items-center justify-between">
        {/* Logo + empresa */}
        <div className="flex items-center gap-4">
          <span className="text-lg font-bold tracking-tight text-gold">
            OperaBot
          </span>
          {company && (
            <div className="hidden sm:block pl-4 border-l border-border">
              <p className="text-sm font-medium text-text-primary">{company.name}</p>
            </div>
          )}
        </div>

        {/* Usuario + logout */}
        <div className="flex items-center gap-4">
          {user && (
            <div className="hidden sm:flex items-center gap-3">
              {/* Avatar */}
              <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border bg-card border-border text-gold">
                {initial}
              </div>
              <div className="text-right">
                <p className="text-sm font-medium leading-none text-text-primary">
                  {user.email}
                </p>
                <p className="text-xs mt-1 text-gold">
                  {ROLE_LABEL[user.role] ?? user.role}
                </p>
              </div>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all duration-150 border-border text-text-secondary hover:border-error hover:text-error"
          >
            <LogOut size={13} strokeWidth={1.5} />
            Salir
          </button>
        </div>
      </div>
    </header>
  );
}
