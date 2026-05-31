"use client";

import { useAuthContext } from "@/components/Auth/AuthProvider";
import { apiFetch } from "@/lib/api";
import { Ticket, TicketNote } from "@/lib/types";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { X, Plus, ChevronDown, ChevronUp } from "lucide-react";

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
  high:   { bg: "rgba(229,62,62,0.08)",  text: "#E53E3E", border: "rgba(229,62,62,0.25)" },
  medium: { bg: "rgba(201,168,76,0.08)", text: "#C9A84C", border: "rgba(201,168,76,0.25)" },
  low:    { bg: "rgba(56,161,105,0.08)", text: "#38A169", border: "rgba(56,161,105,0.25)" },
};

// ── TicketDetail — panel expandible ─────────────────────────────────────────

function TicketDetail({
  ticket,
  onClose,
  onUpdated,
}: {
  ticket: Ticket;
  onClose: () => void;
  onUpdated: () => void;
}) {
  const [notes, setNotes] = useState<TicketNote[]>([]);
  const [noteText, setNoteText] = useState("");
  const [savingNote, setSavingNote] = useState(false);

  const [resolutionMsg, setResolutionMsg] = useState(ticket.resolution_message ?? "");
  const [createFaq, setCreateFaq] = useState(false);
  const [resolving, setResolving] = useState(false);
  const [movingInProgress, setMovingInProgress] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch(`/tickets/${ticket.id}/notes`)
      .then(setNotes)
      .catch(() => {});
  }, [ticket.id]);

  const addNote = async () => {
    if (!noteText.trim()) return;
    setSavingNote(true);
    try {
      const note = await apiFetch(`/tickets/${ticket.id}/notes`, {
        method: "POST",
        body: JSON.stringify({ content: noteText.trim() }),
      });
      setNotes((prev) => [...prev, note]);
      setNoteText("");
    } catch (err: any) {
      setError(err.message || "Error añadiendo nota");
    } finally {
      setSavingNote(false);
    }
  };

  const moveToInProgress = async () => {
    setMovingInProgress(true);
    setError(null);
    try {
      await apiFetch(`/tickets/${ticket.id}`, {
        method: "PATCH",
        body: JSON.stringify({ status: "in_progress" }),
      });
      onUpdated();
      onClose();
    } catch (err: any) {
      setError(err.message || "Error actualizando ticket");
    } finally {
      setMovingInProgress(false);
    }
  };

  const resolveTicket = async () => {
    if (!resolutionMsg.trim()) {
      setError("Escribe una respuesta antes de resolver.");
      return;
    }
    setResolving(true);
    setError(null);
    try {
      await apiFetch(`/tickets/${ticket.id}`, {
        method: "PATCH",
        body: JSON.stringify({ status: "resolved", resolution_message: resolutionMsg.trim() }),
      });
      if (createFaq) {
        await apiFetch("/faqs", {
          method: "POST",
          body: JSON.stringify({
            question: ticket.question,
            answer: resolutionMsg.trim(),
            category: "Tickets",
          }),
        });
      }
      onUpdated();
      onClose();
    } catch (err: any) {
      setError(err.message || "Error resolviendo ticket");
    } finally {
      setResolving(false);
    }
  };

  const pColor = priorityColors[ticket.priority] ?? priorityColors["medium"];
  const canMoveInProgress = ticket.status === "open";
  const canResolve = ticket.status === "in_progress";
  const isResolved = ticket.status === "resolved";

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4"
      style={{ backgroundColor: "rgba(0,0,0,0.7)" }}
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        className="w-full max-w-2xl rounded-2xl border overflow-hidden flex flex-col"
        style={{
          backgroundColor: "#1A1A1A",
          borderColor: "#2A2A2A",
          maxHeight: "90vh",
        }}
      >
        {/* Header */}
        <div
          className="flex items-start justify-between p-5 border-b"
          style={{ borderColor: "#2A2A2A" }}
        >
          <div className="flex-1 min-w-0 pr-4">
            <p className="text-base font-semibold leading-snug" style={{ color: "#F5F5F5" }}>
              {ticket.question}
            </p>
            <div className="flex flex-wrap items-center gap-2 mt-2">
              <span
                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border"
                style={{ backgroundColor: pColor.bg, color: pColor.text, borderColor: pColor.border }}
              >
                {ticket.priority}
              </span>
              <span
                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border"
                style={{ backgroundColor: "rgba(255,255,255,0.04)", color: "#888888", borderColor: "#2A2A2A" }}
              >
                {statusLabels[ticket.status]}
              </span>
              {ticket.user_email && (
                <span className="text-xs" style={{ color: "#555555" }}>
                  por {ticket.user_email}
                </span>
              )}
              <span className="text-xs" style={{ color: "#555555" }}>
                {new Date(ticket.created_at).toLocaleString()}
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="shrink-0 p-1 rounded-lg transition-colors"
            style={{ color: "#888888" }}
            onMouseEnter={(e) => ((e.currentTarget as HTMLButtonElement).style.color = "#F5F5F5")}
            onMouseLeave={(e) => ((e.currentTarget as HTMLButtonElement).style.color = "#888888")}
          >
            <X size={16} strokeWidth={1.75} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-6">
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

          {/* Resolved message */}
          {isResolved && ticket.resolution_message && (
            <div
              className="rounded-xl border p-4"
              style={{ backgroundColor: "rgba(56,161,105,0.06)", borderColor: "rgba(56,161,105,0.2)" }}
            >
              <p className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: "#38A169" }}>
                Respuesta al usuario
              </p>
              <p className="text-sm" style={{ color: "#F5F5F5" }}>
                {ticket.resolution_message}
              </p>
            </div>
          )}

          {/* Notes section */}
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: "#888888" }}>
              Notas internas ({notes.length})
            </p>
            <div className="space-y-2 mb-3">
              {notes.length === 0 && (
                <p className="text-xs italic" style={{ color: "#555555" }}>Sin notas aún.</p>
              )}
              {notes.map((n) => (
                <div
                  key={n.id}
                  className="rounded-lg border px-4 py-3"
                  style={{ backgroundColor: "#111111", borderColor: "#2A2A2A" }}
                >
                  <p className="text-sm" style={{ color: "#F5F5F5" }}>{n.content}</p>
                  <p className="text-xs mt-1" style={{ color: "#555555" }}>
                    {n.author_email ?? "Admin"} · {new Date(n.created_at).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
            {!isResolved && (
              <div className="flex gap-2">
                <textarea
                  value={noteText}
                  onChange={(e) => setNoteText(e.target.value)}
                  placeholder="Añadir nota interna..."
                  rows={2}
                  className="input flex-1 resize-none"
                />
                <button
                  onClick={addNote}
                  disabled={savingNote || !noteText.trim()}
                  className="btn btn-secondary btn-sm self-end"
                >
                  <Plus size={14} strokeWidth={2} />
                  {savingNote ? "..." : "Añadir"}
                </button>
              </div>
            )}
          </div>

          {/* Move to In Progress */}
          {canMoveInProgress && (
            <div className="divider" />
          )}
          {canMoveInProgress && (
            <button
              onClick={moveToInProgress}
              disabled={movingInProgress}
              className="btn btn-secondary w-full"
            >
              {movingInProgress ? "Guardando..." : "Mover a In Progress"}
            </button>
          )}

          {/* Resolution section */}
          {canResolve && (
            <>
              <div className="divider" />
              <div className="space-y-3">
                <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "#888888" }}>
                  Resolución
                </p>
                <textarea
                  value={resolutionMsg}
                  onChange={(e) => setResolutionMsg(e.target.value)}
                  placeholder="Escribe la respuesta al usuario antes de resolver..."
                  rows={4}
                  className="input w-full resize-none"
                />
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={createFaq}
                    onChange={(e) => setCreateFaq(e.target.checked)}
                    className="rounded"
                    style={{ accentColor: "#C9A84C" }}
                  />
                  <span className="text-sm" style={{ color: "#888888" }}>
                    Crear FAQ con esta resolución
                  </span>
                </label>
                <button
                  onClick={resolveTicket}
                  disabled={resolving || !resolutionMsg.trim()}
                  className="btn btn-primary w-full"
                >
                  {resolving ? "Resolviendo..." : "Resolver y notificar"}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Página principal ─────────────────────────────────────────────────────────

export default function AdminTicketsPage() {
  const { user } = useAuthContext();
  const router = useRouter();

  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);

  useEffect(() => {
    if (user && user.role === "user") router.push("/dashboard");
  }, [user, router]);

  const loadTickets = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiFetch("/tickets/");
      setTickets(data || []);
    } catch (err: any) {
      setError(err.message || "No se pudieron cargar los tickets.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadTickets();
  }, []);

  if (user && user.role === "user") return null;

  const renderColumn = (status: string, title: string) => {
    const cols = tickets.filter((t) => t.status === status);
    return (
      <div className="space-y-3">
        <div
          className="rounded-lg border px-4 py-3"
          style={{ backgroundColor: "#111111", borderColor: "#2A2A2A" }}
        >
          <h2 className="text-xs font-semibold uppercase tracking-widest" style={{ color: "#888888" }}>
            {title}
          </h2>
          <p className="text-xs mt-0.5" style={{ color: "#555555" }}>
            {cols.length} {cols.length === 1 ? "ticket" : "tickets"}
          </p>
        </div>

        <div className="space-y-3">
          {cols.length === 0 ? (
            <div
              className="rounded-xl border-dashed border px-4 py-6 text-center text-sm"
              style={{ borderColor: "#2A2A2A", color: "#555555" }}
            >
              Sin tickets
            </div>
          ) : (
            cols.map((ticket) => {
              const pColor = priorityColors[ticket.priority] ?? priorityColors["medium"];
              return (
                <button
                  key={ticket.id}
                  type="button"
                  onClick={() => setSelectedTicket(ticket)}
                  className="card rounded-xl p-4 space-y-3 w-full text-left transition-all duration-150"
                  style={{ cursor: "pointer" }}
                  onMouseEnter={(e) =>
                    ((e.currentTarget as HTMLButtonElement).style.borderColor = "#3A3A3A")
                  }
                  onMouseLeave={(e) =>
                    ((e.currentTarget as HTMLButtonElement).style.borderColor = "#2A2A2A")
                  }
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
                    <span className="text-xs" style={{ color: "#555555" }}>
                      {new Date(ticket.created_at).toLocaleDateString()}
                    </span>
                    {ticket.user_email && (
                      <span className="text-xs truncate max-w-[120px]" style={{ color: "#555555" }}>
                        {ticket.user_email}
                      </span>
                    )}
                  </div>
                </button>
              );
            })
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight" style={{ color: "#F5F5F5" }}>
          Kanban de Tickets
        </h1>
        <p className="text-sm mt-1" style={{ color: "#888888" }}>
          Haz click en una tarjeta para gestionarla.
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
            <div key={i} className="h-40 rounded-xl animate-pulse" style={{ backgroundColor: "#1A1A1A" }} />
          ))}
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-3">
          {renderColumn("open", "Open")}
          {renderColumn("in_progress", "In Progress")}
          {renderColumn("resolved", "Resolved")}
        </div>
      )}

      {selectedTicket && (
        <TicketDetail
          ticket={selectedTicket}
          onClose={() => setSelectedTicket(null)}
          onUpdated={() => {
            loadTickets();
            setSelectedTicket(null);
          }}
        />
      )}
    </div>
  );
}
