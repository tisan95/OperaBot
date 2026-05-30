"use client";

import { useAuthContext } from "@/components/Auth/AuthProvider";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navigation = [
  { name: "Chat", href: "/chat", icon: "💬" },
  { name: "FAQ", href: "/faq", icon: "❓" },
  { name: "Documents", href: "/documents", icon: "📄" },
];

const adminNavigation = [
  { name: "Tickets", href: "/tickets", icon: "🧾" },
  { name: "Usuarios", href: "/users", icon: "👥" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuthContext();

  return (
    <aside className="w-64 bg-slate-900 text-white shadow-lg">
      <nav className="p-6 space-y-2">
        <Link
          href="/dashboard"
          className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition mb-4 border-b border-slate-700 pb-4 ${
            pathname === "/dashboard"
              ? "bg-indigo-600 font-semibold"
              : "hover:bg-slate-800"
          }`}
        >
          <span className="text-xl">📊</span>
          <span>Panel de Control</span>
        </Link>
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition ${
                isActive
                  ? "bg-indigo-600 font-semibold"
                  : "hover:bg-slate-800"
              }`}
            >
              <span className="text-xl">{item.icon}</span>
              <span>{item.name}</span>
            </Link>
          );
        })}
        {user?.role === "admin" && (
          <div className="pt-4 border-t border-slate-700 space-y-2">
            {adminNavigation.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition ${
                    isActive
                      ? "bg-indigo-600 font-semibold"
                      : "hover:bg-slate-800"
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
