"use client";

import { useAuthContext } from "@/components/Auth/AuthProvider";
import { apiFetch } from "@/lib/api";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import {
  LayoutDashboard,
  MessageSquare,
  BookOpen,
  FileText,
  Ticket,
  Users,
  HelpCircle,
} from "lucide-react";

const userNav = [
  { name: "Panel de Control", href: "/dashboard",  icon: LayoutDashboard },
  { name: "Chat",             href: "/chat",        icon: MessageSquare   },
  { name: "FAQ",              href: "/faq",         icon: BookOpen        },
];

const adminNav = [
  { name: "Documentos", href: "/documents",     icon: FileText },
  { name: "Tickets",    href: "/admin/tickets", icon: Ticket   },
];

const superAdminNav = [
  { name: "Usuarios", href: "/users", icon: Users },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuthContext();
  const isAdmin      = user?.role === "admin" || user?.role === "super_admin";
  const isSuperAdmin = user?.role === "super_admin";
  const isUser       = user?.role === "user";

  const [hasTickets, setHasTickets] = useState(false);
  const [hasPendingTickets, setHasPendingTickets] = useState(false);

  useEffect(() => {
    if (!isUser) return;
    apiFetch("/tickets/my")
      .then((data) => {
        if (!Array.isArray(data) || data.length === 0) return;
        setHasTickets(true);
        setHasPendingTickets(
          data.some((t: any) => t.status === "open" || t.status === "in_progress")
        );
      })
      .catch(() => {});
  }, [isUser]);

  const renderLinks = (items: { name: string; href: string; icon: React.ElementType }[]) =>
    items.map(({ name, href, icon: Icon }) => {
      const active = pathname === href;
      return (
        <Link
          key={href}
          href={href}
          className={`
            relative flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium
            transition-all duration-150
            ${active
              ? "bg-[#1A1A1A] text-[#C9A84C] border-l-[3px] border-[#C9A84C] pl-[13px]"
              : "text-[#888888] hover:text-[#C9A84C] hover:bg-[#111111] border-l-[3px] border-transparent pl-[13px]"
            }
          `}
        >
          <Icon size={16} strokeWidth={1.75} className={active ? "text-[#C9A84C]" : "text-[#555555]"} />
          {name}
        </Link>
      );
    });

  return (
    <aside
      className="w-60 shrink-0 flex flex-col border-r"
      style={{ backgroundColor: "#0A0A0A", borderColor: "#2A2A2A", minHeight: "calc(100vh - 57px)" }}
    >
      <nav className="flex flex-col gap-0.5 p-4 pt-6">
        {renderLinks(userNav)}

        {/* Mis Consultas — solo si el user tiene tickets */}
        {isUser && hasTickets && (
          <Link
            href="/my-tickets"
            className={`
              relative flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium
              transition-all duration-150
              ${pathname === "/my-tickets"
                ? "bg-[#1A1A1A] text-[#C9A84C] border-l-[3px] border-[#C9A84C] pl-[13px]"
                : "text-[#888888] hover:text-[#C9A84C] hover:bg-[#111111] border-l-[3px] border-transparent pl-[13px]"
              }
            `}
          >
            <HelpCircle size={16} strokeWidth={1.75} className={pathname === "/my-tickets" ? "text-[#C9A84C]" : "text-[#555555]"} />
            Mis Consultas
            {hasPendingTickets && (
              <span
                className="ml-auto w-2 h-2 rounded-full shrink-0"
                style={{ backgroundColor: "#C9A84C" }}
              />
            )}
          </Link>
        )}

        {isAdmin && (
          <>
            <div className="my-3 border-t" style={{ borderColor: "#2A2A2A" }} />
            {renderLinks(adminNav)}
          </>
        )}

        {isSuperAdmin && (
          <>
            <div className="my-3 border-t" style={{ borderColor: "#2A2A2A" }} />
            {renderLinks(superAdminNav)}
          </>
        )}
      </nav>
    </aside>
  );
}
