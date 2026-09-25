"use client";

import { useAuthContext } from "@/components/Auth/AuthProvider";
import { useSidebar } from "@/components/Shared/SidebarContext";
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
  X,
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
  const { mobileOpen, setMobileOpen } = useSidebar();

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

  const close = () => setMobileOpen(false);

  // Clases para un nav item individual
  const linkBase = (active: boolean) => `
    group relative flex items-center py-2.5 rounded-lg text-sm font-medium
    transition-all duration-150
    justify-center xl:justify-start xl:gap-3
    ${active
      ? "bg-card text-gold xl:border-l-[3px] xl:border-gold xl:pl-[13px] xl:pr-4"
      : "text-text-secondary hover:text-gold hover:bg-card xl:border-l-[3px] xl:border-transparent xl:pl-[13px] xl:pr-4"
    }
  `;

  const renderLinks = (items: { name: string; href: string; icon: React.ElementType }[]) =>
    items.map(({ name, href, icon: Icon }) => {
      const active = pathname === href;
      return (
        <Link
          key={href}
          href={href}
          onClick={close}
          className={linkBase(active)}
        >
          <Icon
            size={16}
            strokeWidth={1.5}
            className={`shrink-0 ${active ? "text-gold" : "text-muted"}`}
          />
          {/* Texto: visible en mobile overlay (mobileOpen) o en xl+ */}
          <span className={`${mobileOpen ? "inline" : "hidden xl:inline"} flex-1 truncate`}>
            {name}
          </span>
          {/* Tooltip CSS para modo icon-only (md a xl) */}
          <span className="
            pointer-events-none absolute left-full ml-3 px-2.5 py-1.5
            rounded-lg text-xs font-medium whitespace-nowrap shadow-lg z-[60]
            bg-surface border border-border text-text-primary
            opacity-0 group-hover:opacity-100 transition-opacity duration-150
            xl:hidden
          ">
            {name}
          </span>
        </Link>
      );
    });

  const myTicketsActive = pathname === "/my-tickets";

  return (
    <>
      {/* Backdrop mobile */}
      <div
        className={`
          fixed inset-0 z-40 bg-black/60 md:hidden transition-opacity duration-200
          ${mobileOpen ? "opacity-100" : "opacity-0 pointer-events-none"}
        `}
        onClick={close}
      />

      <aside
        className={`
          flex flex-col shrink-0 border-r bg-bg border-border
          /* Mobile: fixed overlay deslizable */
          fixed inset-y-0 left-0 z-50 w-72
          transform transition-transform duration-200 ease-in-out
          ${mobileOpen ? "translate-x-0" : "-translate-x-full"}
          /* md+: estático en el flujo, anula el fixed */
          md:static md:inset-auto md:z-auto md:transform-none
          /* Anchos según breakpoint */
          md:w-16 xl:w-60
        `}
      >
        {/* Cabecera visible solo en overlay mobile */}
        <div className="md:hidden flex items-center justify-between px-4 py-3 border-b border-border shrink-0">
          <span className="text-sm font-bold text-gold">OperaBot</span>
          <button
            onClick={close}
            className="p-1 rounded-lg text-text-secondary hover:text-text-primary transition-colors"
          >
            <X size={16} strokeWidth={1.5} />
          </button>
        </div>

        <nav className="flex flex-col gap-0.5 p-4 md:p-2 xl:p-4 pt-4 md:pt-4 xl:pt-6 flex-1 overflow-y-auto">
          {renderLinks(userNav)}

          {/* Mis Consultas — solo si el user tiene tickets */}
          {isUser && hasTickets && (
            <Link
              href="/my-tickets"
              onClick={close}
              className={linkBase(myTicketsActive)}
            >
              <div className="relative shrink-0">
                <HelpCircle
                  size={16}
                  strokeWidth={1.5}
                  className={myTicketsActive ? "text-gold" : "text-muted"}
                />
                {/* Dot en modo icon-only (md) */}
                {hasPendingTickets && (
                  <span className="absolute -top-0.5 -right-0.5 w-1.5 h-1.5 rounded-full bg-gold xl:hidden" />
                )}
              </div>
              <span className={`${mobileOpen ? "inline" : "hidden xl:inline"} flex-1 truncate`}>
                Mis Consultas
              </span>
              {/* Dot en modo full (xl o mobile overlay) */}
              {hasPendingTickets && (
                <span className={`
                  ml-auto w-2 h-2 rounded-full shrink-0 bg-gold
                  ${mobileOpen ? "inline-block" : "hidden xl:inline-block"}
                `} />
              )}
              {/* Tooltip para icon-only */}
              <span className="
                pointer-events-none absolute left-full ml-3 px-2.5 py-1.5
                rounded-lg text-xs font-medium whitespace-nowrap shadow-lg z-[60]
                bg-surface border border-border text-text-primary
                opacity-0 group-hover:opacity-100 transition-opacity duration-150
                xl:hidden
              ">
                Mis Consultas
              </span>
            </Link>
          )}

          {isAdmin && (
            <>
              <div className="my-2 xl:my-3 border-t border-border" />
              {renderLinks(adminNav)}
            </>
          )}

          {isSuperAdmin && (
            <>
              <div className="my-2 xl:my-3 border-t border-border" />
              {renderLinks(superAdminNav)}
            </>
          )}
        </nav>
      </aside>
    </>
  );
}
