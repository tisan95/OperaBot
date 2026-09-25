"use client";

import { useAuthContext } from "@/components/Auth/AuthProvider";
import { apiFetch } from "@/lib/api";
import { Ticket, TicketNote } from "@/lib/types";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { X, Plus } from "lucide-react";
import RichEditor from "@/components/Shared/RichEditor";
import EmptyState from "@/components/Shared/EmptyState";
import { sanitizeHtml } from "@/lib/sanitize";
import { Inbox } from "lucide-react";

const isEmptyHtml = (html: string) =>
  !html || html.replace(/<[^>]*>/g, "").trim().length === 0;

const statusLabels: Record<string, string> = {
  open:        "Abierto",
  in_progress: "En Progreso",
  resolved:    "Resuelto",
};

const priorityLabels: Record<string, string> = {
  high:   "Alta",
  medium: "Media",
  low:    "Baja",
};

const priorityClasses: Record<string, string> = {
  high:   "bg-error/8 text-error border-error/25",
  medium: "bg-gold/8 text-gold border-gold/25",
  low:    "bg-success/8 text-success border-success/25",
};

// ── TicketDetail ─────────────────────────────────────────────────────────────

function TicketDetail({
  ticket,
  onClose,
  onUpdated,
}: {
  ticket: Ticket;
  onClose: () => void;
  onUpdated: () => void;
}) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const [notes, setNotes] = useState<TicketNote[]>([]);
  const [noteText, setNoteText] = useState("");
  const [savingNote, setSavingNote] = useState(false);
  const [resolutionMsg, setResolutionMsg] = useState(ticket.resolution_message ?? "");
  const [createFaq, setCreateFaq] = useState(false);
  const [resolving, setResolving] = useState(false);
  const [movingInProgress, setMovingInProgress] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Escape para cerrar
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [onClose]);

  // Focus trap
  useEffect(() => {
    const el = dialogRef.current;
    if (!el) return;
    const focusable = Array.from(
      el.querySelectorAll<HTMLElement>(
        'button:not([disabled]),input:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])'
      )
    );
    focusable[0]?.focus();
    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== "Tab" || focusable.length === 0) return;
      const first = focusable[0];
      const last  = focusable[focusable.length - 1];
      if (e.shiftKey) {
        if (document.activeElement === first) { e.preventDefault(); last.focus(); }
      } else {
        if (document.activeElement === last)  { e.preventDefault(); first.focus(); }
      }
    };
    document.addEventListener("keydown", handleTab);
    return () => document.removeEventListener("keydown", handleTab);
  }, []);

  useEffect(() => {
    apiFetch(`/tickets/${ticket.id}/notes`).then(setNotes).catch(() => {});
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
          body: JSON.stringify({ question: ticket.question, answer: resolutionMsg.trim(), category: "Tickets" }),
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

  const pClasses   = priorityClasses[ticket.priority] ?? priorityClasses["medium"];
  const canMoveInProgress = ticket.status === "open";
  const canResolve        = ticket.status === "in_progress";
  const isResolved        = ticket.status === "resolved";

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 animate-backdropIn"
      style={{ backgroundColor: "rgba(0,0,0,0.7)" }}
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-label={ticket.question}
        className="w-full max-w-2xl rounded-2xl border overflow-hidden flex flex-col bg-card border-border animate-modalIn"
        style={{ maxHeight: "90vh" }}
      >
        {/* Header */}
        <div className="flex items-start justify-between p-5 border-b border-border shrink-0">
          <div className="flex-1 min-w-0 pr-4">
            <p className="text-base font-semibold leading-snug text-text-primary">
              {ticket.question}
            </p>
            <div className="flex flex-wrap items-center gap-2 mt-2">
              <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${pClasses}`}>
                {priorityLabels[ticket.priority] ?? ticket.priority}
              </span>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border bg-white/[0.04] text-text-secondary border-border">
                {statusLabels[ticket.status]}
              </span>
              {ticket.user_email && (
                <span className="text-xs text-muted">por {ticket.user_email}</span>
              )}
              <span className="text-xs text-muted">
                {new Date(ticket.created_at).toLocaleString()}
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="shrink-0 p-1 rounded-lg transition-colors text-text-secondary hover:text-text-primary"
            aria-label="Cerrar"
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

          {/* Respuesta al usuario (resolved) */}
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

          {/* Notas internas */}
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider mb-3 text-text-secondary">
              Notas internas ({notes.length})
            </p>
            <div className="space-y-2 mb-3">
              {notes.length === 0 && (
                <p className="text-xs italic text-muted">Sin notas aún.</p>
              )}
              {notes.map((n) => (
                <div key={n.id} className="rounded-lg border px-4 py-3 bg-surface border-border">
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
                <RichEditor content={noteText} onChange={setNoteText} placeholder="Añadir nota interna..." minHeight={80} />
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

          {canMoveInProgress && <div className="divider" />}
          {canMoveInProgress && (
            <button onClick={moveToInProgress} disabled={movingInProgress} className="btn btn-secondary w-full">
              {movingInProgress ? "Guardando..." : "Mover a En Progreso"}
            </button>
          )}

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
  const router   = useRouter();

  const [tickets, setTickets]             = useState<Ticket[]>([]);
  const [isLoading, setIsLoading]         = useState(true);
  const [error, setError]                 = useState<string | null>(null);
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

  useEffect(() => { loadTickets(); }, []);

  if (user && user.role === "user") return null;

  const renderColumn = (status: string, title: string) => {
    const cols = tickets.filter((t) => t.status === status);
    return (
      /* Columna: scroll interno + sticky header */
      <div className="flex flex-col overflow-y-auto max-h-[calc(100vh-280px)] rounded-xl">
        {/* Header sticky dentro del scroll container */}
        <div className="sticky top-0 z-10 rounded-t-lg border border-b-0 px-4 py-3 bg-surface border-border shrink-0">
          <h2 className="text-xs font-semibold uppercase tracking-widest text-text-secondary">
            {title}
          </h2>
          <p className="text-xs mt-0.5 text-muted">
            {cols.length} {cols.length === 1 ? "ticket" : "tickets"}
          </p>
        </div>

        {/* Contenido scrollable */}
        <div className="flex flex-col gap-3 p-3 border border-t-0 rounded-b-xl border-border min-h-[80px]">
          {cols.length === 0 ? (
            <EmptyState
              icon={Inbox}
              title="Sin tickets"
              description="Nada en esta columna por ahora."
            />
          ) : (
            cols.map((ticket) => {
              const pClasses = priorityClasses[ticket.priority] ?? priorityClasses["medium"];
              return (
                <button
                  key={ticket.id}
                  type="button"
                  onClick={() => setSelectedTicket(ticket)}
                  className="card rounded-xl p-4 space-y-3 w-full text-left transition-all duration-150 cursor-pointer hover:border-[#3A3A3A] hover:bg-card-hover"
                >
                  <p className="text-sm font-medium leading-snug text-text-primary">
                    {ticket.question}
                  </p>
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${pClasses}`}>
                      {priorityLabels[ticket.priority] ?? ticket.priority}
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
          Haz clic en una tarjeta para gestionarla.
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
          {renderColumn("open",        "Abierto")}
          {renderColumn("in_progress", "En Progreso")}
          {renderColumn("resolved",    "Resuelto")}
        </div>
      )}

      {selectedTicket && (
        <TicketDetail
          ticket={selectedTicket}
          onClose={() => setSelectedTicket(null)}
          onUpdated={() => { loadTickets(); setSelectedTicket(null); }}
        />
      )}
    </div>
  );
}
