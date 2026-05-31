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
    <header
      className="sticky top-0 z-40 border-b"
      style={{ backgroundColor: "#111111", borderColor: "#2A2A2A" }}
    >
      <div className="px-6 h-14 flex items-center justify-between">
        {/* Logo + empresa */}
        <div className="flex items-center gap-4">
          <span className="text-lg font-bold tracking-tight" style={{ color: "#C9A84C" }}>
            OperaBot
          </span>
          {company && (
            <div className="hidden sm:block pl-4 border-l" style={{ borderColor: "#2A2A2A" }}>
              <p className="text-sm font-medium" style={{ color: "#F5F5F5" }}>{company.name}</p>
            </div>
          )}
        </div>

        {/* Usuario + logout */}
        <div className="flex items-center gap-4">
          {user && (
            <div className="hidden sm:flex items-center gap-3">
              {/* Avatar */}
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border"
                style={{ backgroundColor: "#1A1A1A", borderColor: "#2A2A2A", color: "#C9A84C" }}
              >
                {initial}
              </div>
              <div className="text-right">
                <p className="text-sm font-medium leading-none" style={{ color: "#F5F5F5" }}>
                  {user.email}
                </p>
                <p className="text-xs mt-1" style={{ color: "#C9A84C" }}>
                  {ROLE_LABEL[user.role] ?? user.role}
                </p>
              </div>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all duration-150"
            style={{ borderColor: "#2A2A2A", color: "#888888" }}
            onMouseEnter={e => {
              (e.currentTarget as HTMLButtonElement).style.borderColor = "#E53E3E";
              (e.currentTarget as HTMLButtonElement).style.color = "#E53E3E";
            }}
            onMouseLeave={e => {
              (e.currentTarget as HTMLButtonElement).style.borderColor = "#2A2A2A";
              (e.currentTarget as HTMLButtonElement).style.color = "#888888";
            }}
          >
            <LogOut size={13} />
            Salir
          </button>
        </div>
      </div>
    </header>
  );
}
