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

export default function AdminTicketsPage() {
  const { user } = useAuthContext();
  const router = useRouter();

  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  useEffect(() => {
    if (user && user.role !== "admin") {
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
      <div className="space-y-4">
        <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
          <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-700">
            {title}
          </h2>
          <p className="text-xs text-slate-500 mt-1">{columnTickets.length} tickets</p>
        </div>

        <div className="space-y-4">
          {columnTickets.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-300 bg-white px-4 py-6 text-center text-sm text-slate-500">
              No hay tickets en esta columna.
            </div>
          ) : (
            columnTickets.map((ticket) => (
              <div
                key={ticket.id}
                className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
              >
                <p className="text-sm font-semibold text-slate-900">{ticket.question}</p>
                <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
                  <span className="rounded-full bg-indigo-100 px-2.5 py-1 text-indigo-700">
                    {ticket.priority}
                  </span>
                  <span className="rounded-full bg-slate-100 px-2.5 py-1 text-slate-600">
                    {statusLabels[ticket.status] || ticket.status}
                  </span>
                  <span className="rounded-full bg-slate-100 px-2.5 py-1 text-slate-600">
                    {new Date(ticket.created_at).toLocaleString()}
                  </span>
                </div>

                {nextStatus[ticket.status] ? (
                  <button
                    type="button"
                    onClick={() => changeStatus(ticket)}
                    disabled={updatingId === ticket.id}
                    className="mt-4 inline-flex items-center justify-center rounded-lg bg-slate-900 px-3 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {updatingId === ticket.id ? "Guardando..." : `Mover a ${statusLabels[nextStatus[ticket.status]]}`}
                  </button>
                ) : null}
              </div>
            ))
          )}
        </div>
      </div>
    );
  };

  if (user && user.role !== "admin") return null;

  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Kanban de Tickets</h1>
          <p className="mt-2 text-sm text-slate-600">
            Revisa los tickets creados automáticamente por el chat y mueve su estado.
          </p>
        </div>
      </div>

      {error ? (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          {error}
        </div>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-3">
        {renderColumn("open", "Open")}
        {renderColumn("in_progress", "In Progress")}
        {renderColumn("resolved", "Resolved")}
      </div>

      {isLoading ? (
        <div className="rounded-xl border border-slate-200 bg-white p-6 text-center text-slate-600">
          Cargando tickets...
        </div>
      ) : null}
    </div>
  );
}
