"use client";

import { useAuthContext } from "@/components/Auth/AuthProvider";
import { apiFetch } from "@/lib/api";
import { Ticket, TicketNote } from "@/lib/types";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { X, Plus, ChevronDown, ChevronUp } from "lucide-react";
import RichEditor from "@/components/Shared/RichEditor";
import { sanitizeHtml } from "@/lib/sanitize";

const isEmptyHtml = (html: string) =>
  !html || html.replace(/<[^>]*>/g, "").trim().length === 0;

const statusLabels: Record<string, string> = {
  open: "Open",
  in_progress: "In Progress",
  resolved: "Resolved",
};

const priorityClasses: Record<string, string> = {
  high:   "bg-error/8 text-error border-error/25",
  medium: "bg-gold/8 text-gold border-gold/25",
  low:    "bg-success/8 text-success border-success/25",
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
    if (isEmptyHtml(resolutionMsg)) {
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

  const pClasses = priorityClasses[ticket.priority] ?? priorityClasses["medium"];
  const canMoveInProgress = ticket.status === "open";
  const canResolve = ticket.status === "in_progress";
  const isResolved = ticket.status === "resolved";

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 bg-black/70"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        className="w-full max-w-2xl rounded-2xl border overflow-hidden flex flex-col bg-card border-border"
        style={{ maxHeight: "90vh" }}
      >
        {/* Header */}
        <div className="flex items-start justify-between p-5 border-b border-border">
          <div className="flex-1 min-w-0 pr-4">
            <p className="text-base font-semibold leading-snug text-text-primary">
              {ticket.question}
            </p>
            <div className="flex flex-wrap items-center gap-2 mt-2">
              <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${pClasses}`}>
                {ticket.priority}
              </span>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border bg-white/[0.04] text-text-secondary border-border">
                {statusLabels[ticket.status]}
              </span>
              {ticket.user_email && (
                <span className="text-xs text-muted">
                  por {ticket.user_email}
                </span>
              )}
              <span className="text-xs text-muted">
                {new Date(ticket.created_at).toLocaleString()}
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="shrink-0 p-1 rounded-lg transition-colors text-text-secondary hover:text-text-primary"
          >
            <X size={16} strokeWidth={1.5} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-6">
          {error && (
            <div className="px-4 py-3 rounded-lg border text-sm bg-error/8 border-error/30 text-error">
              {error}
            </div>
          )}

          {/* Resolved message */}
          {isResolved && ticket.resolution_message && (
            <div className="rounded-xl border p-4 bg-success/6 border-success/20">
              <p className="text-xs font-semibold uppercase tracking-wider mb-2 text-success">
                Respuesta al usuario
              </p>
              <div
                className="rich-content text-sm"
                dangerouslySetInnerHTML={{ __html: sanitizeHtml(ticket.resolution_message) }}
              />
            </div>
          )}

          {/* Notes section */}
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider mb-3 text-text-secondary">
              Notas internas ({notes.length})
            </p>
            <div className="space-y-2 mb-3">
              {notes.length === 0 && (
                <p className="text-xs italic text-muted">Sin notas aún.</p>
              )}
              {notes.map((n) => (
                <div
                  key={n.id}
                  className="rounded-lg border px-4 py-3 bg-surface border-border"
                >
                  <div
                    className="rich-content text-sm"
                    dangerouslySetInnerHTML={{ __html: sanitizeHtml(n.content) }}
                  />
                  <p className="text-xs mt-1 text-muted">
                    {n.author_email ?? "Admin"} · {new Date(n.created_at).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
            {!isResolved && (
              <div className="space-y-2">
                <RichEditor
                  content={noteText}
                  onChange={setNoteText}
                  placeholder="Añadir nota interna..."
                  minHeight={80}
                />
                <button
                  onClick={addNote}
                  disabled={savingNote || isEmptyHtml(noteText)}
                  className="btn btn-secondary btn-sm"
                >
                  <Plus size={14} strokeWidth={1.5} />
                  {savingNote ? "..." : "Añadir nota"}
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
                <p className="text-xs font-semibold uppercase tracking-wider text-text-secondary">
                  Resolución
                </p>
                <RichEditor
                  content={resolutionMsg}
                  onChange={setResolutionMsg}
                  placeholder="Escribe la respuesta al usuario antes de resolver..."
                  minHeight={120}
                />
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={createFaq}
                    onChange={(e) => setCreateFaq(e.target.checked)}
                    className="rounded accent-gold"
                  />
                  <span className="text-sm text-text-secondary">
                    Crear FAQ con esta resolución
                  </span>
                </label>
                <button
                  onClick={resolveTicket}
                  disabled={resolving || isEmptyHtml(resolutionMsg)}
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
        <div className="rounded-lg border px-4 py-3 bg-surface border-border">
          <h2 className="text-xs font-semibold uppercase tracking-widest text-text-secondary">
            {title}
          </h2>
          <p className="text-xs mt-0.5 text-muted">
            {cols.length} {cols.length === 1 ? "ticket" : "tickets"}
          </p>
        </div>

        <div className="space-y-3">
          {cols.length === 0 ? (
            <div className="rounded-xl border-dashed border px-4 py-6 text-center text-sm border-border text-muted">
              Sin tickets
            </div>
          ) : (
            cols.map((ticket) => {
              const pClasses = priorityClasses[ticket.priority] ?? priorityClasses["medium"];
              return (
                <button
                  key={ticket.id}
                  type="button"
                  onClick={() => setSelectedTicket(ticket)}
                  className="card rounded-xl p-4 space-y-3 w-full text-left transition-all duration-150 cursor-pointer hover:border-[#3A3A3A]"
                >
                  <p className="text-sm font-medium leading-snug text-text-primary">
                    {ticket.question}
                  </p>
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${pClasses}`}>
                      {ticket.priority}
                    </span>
                    <span className="text-xs text-muted">
                      {new Date(ticket.created_at).toLocaleDateString()}
                    </span>
                    {ticket.user_email && (
                      <span className="text-xs truncate max-w-[120px] text-muted">
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
        <h1 className="text-2xl font-bold tracking-tight text-text-primary">
          Kanban de Tickets
        </h1>
        <p className="text-sm mt-1 text-text-secondary">
          Haz click en una tarjeta para gestionarla.
        </p>
      </div>

      {error && (
        <div className="px-4 py-3 rounded-lg border text-sm bg-error/8 border-error/30 text-error">
          {error}
        </div>
      )}

      {isLoading ? (
        <div className="grid gap-6 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-40 rounded-xl animate-pulse bg-card" />
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
