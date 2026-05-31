"use client";

import { useAuthContext } from "@/components/Auth/AuthProvider";
import { apiFetch } from "@/lib/api";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface Ticket {
  id: number;
  question: string;
  priority: string;
  status: string;
  created_at: string;
}

const statusLabels: Record<string, string> = {
  open: "Open",
  in_progress: "In Progress",
  resolved: "Resolved",
};

const nextStatus: Record<string, string> = {
  open: "in_progress",
  in_progress: "resolved",
};

const priorityColors: Record<string, { bg: string; text: string; border: string }> = {
  high:   { bg: "rgba(229,62,62,0.08)",   text: "#E53E3E", border: "rgba(229,62,62,0.25)" },
  medium: { bg: "rgba(201,168,76,0.08)",  text: "#C9A84C", border: "rgba(201,168,76,0.25)" },
  low:    { bg: "rgba(56,161,105,0.08)",  text: "#38A169", border: "rgba(56,161,105,0.25)" },
};

export default function AdminTicketsPage() {
  const { user } = useAuthContext();
  const router = useRouter();

  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  useEffect(() => {
    if (user && user.role === "user") {
      router.push("/dashboard");
    }
  }, [user, router]);

  const loadTickets = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await apiFetch("/tickets/");
      setTickets(data || []);
    } catch (err: any) {
      console.error("Error cargando tickets:", err);
      setError(err.message || "No se pudieron cargar los tickets.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadTickets();
  }, []);

  const changeStatus = async (ticket: Ticket) => {
    const target = nextStatus[ticket.status];
    if (!target) return;

    setUpdatingId(ticket.id);
    setError(null);

    try {
      await apiFetch(`/tickets/${ticket.id}`, {
        method: "PATCH",
        body: JSON.stringify({ status: target }),
      });
      await loadTickets();
    } catch (err: any) {
      console.error("Error actualizando status:", err);
      setError(err.message || "Error actualizando el ticket.");
    } finally {
      setUpdatingId(null);
    }
  };

  const renderColumn = (status: string, title: string) => {
    const columnTickets = tickets.filter((ticket) => ticket.status === status);

    return (
      <div className="space-y-3">
        {/* Column header */}
        <div
          className="rounded-lg border px-4 py-3"
          style={{ backgroundColor: "#111111", borderColor: "#2A2A2A" }}
        >
          <h2
            className="text-xs font-semibold uppercase tracking-widest"
            style={{ color: "#888888" }}
          >
            {title}
          </h2>
          <p className="text-xs mt-0.5" style={{ color: "#555555" }}>
            {columnTickets.length} {columnTickets.length === 1 ? "ticket" : "tickets"}
          </p>
        </div>

        {/* Cards */}
        <div className="space-y-3">
          {columnTickets.length === 0 ? (
            <div
              className="rounded-xl border-dashed border px-4 py-6 text-center text-sm"
              style={{ borderColor: "#2A2A2A", color: "#555555" }}
            >
              Sin tickets
            </div>
          ) : (
            columnTickets.map((ticket) => {
              const pColor = priorityColors[ticket.priority] ?? priorityColors["medium"];
              return (
                <div
                  key={ticket.id}
                  className="card rounded-xl p-4 space-y-3"
                >
                  <p className="text-sm font-medium leading-snug" style={{ color: "#F5F5F5" }}>
                    {ticket.question}
                  </p>

                  <div className="flex flex-wrap items-center gap-2">
                    <span
                      className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border"
                      style={{
                        backgroundColor: pColor.bg,
                        color: pColor.text,
                        borderColor: pColor.border,
                      }}
                    >
                      {ticket.priority}
                    </span>
                    <span
                      className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border"
                      style={{
                        backgroundColor: "rgba(255,255,255,0.04)",
                        color: "#888888",
                        borderColor: "#2A2A2A",
                      }}
                    >
                      {new Date(ticket.created_at).toLocaleDateString()}
                    </span>
                  </div>

                  {nextStatus[ticket.status] && (
                    <button
                      type="button"
                      onClick={() => changeStatus(ticket)}
                      disabled={updatingId === ticket.id}
                      className="btn btn-secondary btn-sm w-full"
                    >
                      {updatingId === ticket.id
                        ? "Guardando..."
                        : `Mover a ${statusLabels[nextStatus[ticket.status]]}`}
                    </button>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    );
  };

  if (user && user.role === "user") return null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight" style={{ color: "#F5F5F5" }}>
          Kanban de Tickets
        </h1>
        <p className="text-sm mt-1" style={{ color: "#888888" }}>
          Revisa los tickets del chat y gestiona su estado.
        </p>
      </div>

      {error && (
        <div
          className="px-4 py-3 rounded-lg border text-sm"
          style={{
            backgroundColor: "rgba(229,62,62,0.08)",
            borderColor: "rgba(229,62,62,0.3)",
            color: "#E53E3E",
          }}
        >
          {error}
        </div>
      )}

      {isLoading ? (
        <div className="grid gap-6 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-40 rounded-xl animate-pulse"
              style={{ backgroundColor: "#1A1A1A" }}
            />
          ))}
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-3">
          {renderColumn("open", "Open")}
          {renderColumn("in_progress", "In Progress")}
          {renderColumn("resolved", "Resolved")}
        </div>
      )}
    </div>
  );
}
