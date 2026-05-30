"use client";

import { useAuthContext } from "@/components/Auth/AuthProvider";
import Link from "next/link";
import { usePathname } from "next/navigation";

const userNav = [
  { name: "Panel de Control", href: "/dashboard", icon: "📊" },
  { name: "Chat", href: "/chat", icon: "💬" },
  { name: "FAQ", href: "/faq", icon: "❓" },
];

const adminNav = [
  { name: "Documentos", href: "/documents", icon: "📄" },
  { name: "Tickets", href: "/admin/tickets", icon: "🧾" },
  { name: "Usuarios", href: "/users", icon: "👥" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuthContext();
  const isAdmin = user?.role === "admin";

  return (
    <aside className="w-64 bg-slate-900 text-white shadow-lg">
      <nav className="p-6 space-y-2">
        {userNav.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition ${
                isActive ? "bg-indigo-600 font-semibold" : "hover:bg-slate-800"
              }`}
            >
              <span className="text-xl">{item.icon}</span>
              <span>{item.name}</span>
            </Link>
          );
        })}

        {isAdmin && (
          <div className="pt-4 border-t border-slate-700 space-y-2">
            {adminNav.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition ${
                    isActive ? "bg-indigo-600 font-semibold" : "hover:bg-slate-800"
                  }`}
                >
                  <span className="text-xl">{item.icon}</span>
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </div>
        )}
      </nav>
    </aside>
  );
}
