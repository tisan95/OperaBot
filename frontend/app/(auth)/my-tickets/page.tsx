"use client";

import { apiFetch } from "@/lib/api";
import { Ticket } from "@/lib/types";
import { useEffect, useState } from "react";
import { sanitizeHtml } from "@/lib/sanitize";
import { CircleCheck, Clock, AlertCircle, Inbox } from "lucide-react";
import EmptyState from "@/components/Shared/EmptyState";

const statusConfig = {
  open:        { label: "Pendiente",   icon: AlertCircle, colorClass: "text-gold"           },
  in_progress: { label: "En revisión", icon: Clock,       colorClass: "text-text-secondary" },
  resolved:    { label: "Resuelto",    icon: CircleCheck, colorClass: "text-success"         },
} as const;

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

export default function MyTicketsPage() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch("/tickets/my")
      .then((data) => setTickets(Array.isArray(data) ? data : []))
      .catch((err: any) => setError(err.message || "Error cargando consultas"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-text-primary">
          Mis Consultas
        </h1>
        <p className="text-sm mt-1 text-text-secondary">
          Seguimiento de las preguntas que han sido escaladas al equipo.
        </p>
      </div>

      {error && (
        <div className="px-4 py-3 rounded-lg border text-sm bg-error/8 border-error/30 text-error">
          {error}
        </div>
      )}

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 rounded-xl animate-pulse bg-card" />
          ))}
        </div>
      ) : tickets.length === 0 ? (
        <EmptyState
          icon={Inbox}
          title="Sin consultas escaladas"
          description="Cuando una pregunta en el chat se escale al equipo, aparecerá aquí."
        />
      ) : (
        <div className="space-y-4">
          {tickets.map((ticket) => {
            const cfg = statusConfig[ticket.status as keyof typeof statusConfig] ?? statusConfig.open;
            const Icon = cfg.icon;
            const pClasses = priorityClasses[ticket.priority] ?? priorityClasses["medium"];
            const isResolved = ticket.status === "resolved";

            return (
              <div
                key={ticket.id}
                className={`card card-padding space-y-3 ${isResolved ? "border-success/30" : ""}`}
              >
                {/* Title + meta */}
                <div className="flex items-start gap-3">
                  <Icon size={16} strokeWidth={1.5} className={`${cfg.colorClass} mt-0.5 shrink-0`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-text-primary">
                      {ticket.question}
                    </p>
                    <div className="flex flex-wrap items-center gap-2 mt-1.5">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${pClasses}`}>
                        {priorityLabels[ticket.priority] ?? ticket.priority}
                      </span>
                      <span className={`text-xs ${cfg.colorClass}`}>
                        {cfg.label}
                      </span>
                      <span className="text-xs text-muted">
                        {new Date(ticket.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Resolution */}
                {isResolved && ticket.resolution_message && (
                  <div className="rounded-lg border px-3 py-3 bg-success/6 border-success/20">
                    <p className="text-xs font-semibold mb-1.5 text-success">
                      Respuesta del equipo
                    </p>
                    <div
                      className="rich-content text-sm"
                      dangerouslySetInnerHTML={{ __html: sanitizeHtml(ticket.resolution_message) }}
                    />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
