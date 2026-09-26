"use client";

import { useEffect, useRef, useState } from "react";
import { History, ChevronDown, Plus, Trash2, Check, X } from "lucide-react";

export interface ChatSession {
  id: number;
  title: string | null;
  created_at: string;
  updated_at: string;
}

interface SessionsDropdownProps {
  sessions: ChatSession[];
  activeSessionId: number | null;
  onOpen: () => void;
  onSelect: (id: number) => void;
  onNew: () => void;
  onDelete: (id: number) => void;
}

// Backend sends naive UTC timestamps (no timezone suffix) — force UTC parsing
// so relative times aren't off by the local offset.
function parseUTC(dateStr: string): Date {
  return new Date(/Z$|[+-]\d{2}:\d{2}$/.test(dateStr) ? dateStr : `${dateStr}Z`);
}

function formatRelative(dateStr: string): string {
  const diffMs = Date.now() - parseUTC(dateStr).getTime();
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 1) return "ahora";
  if (diffMin < 60) return `hace ${diffMin}m`;
  const diffH = Math.floor(diffMin / 60);
  if (diffH < 24) return `hace ${diffH}h`;
  const diffD = Math.floor(diffH / 24);
  if (diffD === 1) return "ayer";
  if (diffD < 7) return `hace ${diffD}d`;
  return parseUTC(dateStr).toLocaleDateString("es-ES", { day: "2-digit", month: "short" });
}

export default function SessionsDropdown({
  sessions,
  activeSessionId,
  onOpen,
  onSelect,
  onNew,
  onDelete,
}: SessionsDropdownProps) {
  const [open, setOpen] = useState(false);
  const [confirmingId, setConfirmingId] = useState<number | null>(null);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const handleClick = (e: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) {
        setOpen(false);
        setConfirmingId(null);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [open]);

  const handleToggle = () => {
    const next = !open;
    setOpen(next);
    setConfirmingId(null);
    if (next) onOpen();
  };

  const handleSelect = (id: number) => {
    onSelect(id);
    setOpen(false);
    setConfirmingId(null);
  };

  const handleNew = () => {
    onNew();
    setOpen(false);
    setConfirmingId(null);
  };

  return (
    <div ref={rootRef} className="relative">
      <button
        onClick={handleToggle}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors border-border text-text-secondary hover:text-text-primary hover:border-gold/30"
      >
        <History size={13} strokeWidth={1.5} />
        Recientes
        <ChevronDown size={13} strokeWidth={1.5} className={open ? "rotate-180 transition-transform" : "transition-transform"} />
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-72 z-40 rounded-xl border overflow-hidden bg-surface border-border shadow-lg animate-modalIn">
          <button
            onClick={handleNew}
            className="w-full flex items-center gap-2 px-4 py-3 text-sm font-medium border-b transition-colors border-border text-gold hover:bg-card"
          >
            <Plus size={14} strokeWidth={1.5} />
            Nueva conversación
          </button>

          <div className="max-h-72 overflow-y-auto">
            {sessions.length === 0 && (
              <p className="px-4 py-4 text-xs text-center text-text-secondary">
                No hay conversaciones aún.
              </p>
            )}

            {sessions.map((s) => (
              <div
                key={s.id}
                className={`flex items-center gap-2 px-3 py-2.5 border-b last:border-b-0 border-border ${
                  s.id === activeSessionId ? "bg-card" : ""
                }`}
              >
                {confirmingId === s.id ? (
                  <div className="flex items-center justify-between w-full gap-2">
                    <span className="text-xs text-text-secondary">¿Borrar?</span>
                    <div className="flex items-center gap-1.5">
                      <button
                        onClick={() => {
                          onDelete(s.id);
                          setConfirmingId(null);
                        }}
                        className="p-1 rounded border bg-error/8 border-error/30 text-error"
                        aria-label="Confirmar borrado"
                      >
                        <Check size={13} strokeWidth={1.5} />
                      </button>
                      <button
                        onClick={() => setConfirmingId(null)}
                        className="p-1 rounded border border-border text-text-secondary"
                        aria-label="Cancelar"
                      >
                        <X size={13} strokeWidth={1.5} />
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <button
                      onClick={() => handleSelect(s.id)}
                      className="flex-1 min-w-0 text-left"
                    >
                      <p className={`text-sm truncate ${s.id === activeSessionId ? "text-gold" : "text-text-primary"}`}>
                        {s.title || "Nueva conversación"}
                      </p>
                      <p className="text-xs mt-0.5 text-text-secondary">
                        {formatRelative(s.updated_at)}
                      </p>
                    </button>
                    <button
                      onClick={() => setConfirmingId(s.id)}
                      className="shrink-0 p-1.5 rounded transition-colors text-text-secondary hover:text-error"
                      aria-label="Borrar conversación"
                    >
                      <Trash2 size={13} strokeWidth={1.5} />
                    </button>
                  </>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
