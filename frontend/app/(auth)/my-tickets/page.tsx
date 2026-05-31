"use client";

import { apiFetch } from "@/lib/api";
import { Ticket } from "@/lib/types";
import { useEffect, useState } from "react";
import { sanitizeHtml } from "@/lib/sanitize";
import { CircleCheck, Clock, AlertCircle } from "lucide-react";

const statusConfig = {
  open:        { label: "Pendiente",   icon: AlertCircle, color: "#C9A84C" },
  in_progress: { label: "En revisión", icon: Clock,       color: "#888888" },
  resolved:    { label: "Resuelto",    icon: CircleCheck, color: "#38A169" },
} as const;

const priorityColors: Record<string, { bg: string; text: string; border: string }> = {
  high:   { bg: "rgba(229,62,62,0.08)",  text: "#E53E3E", border: "rgba(229,62,62,0.25)" },
  medium: { bg: "rgba(201,168,76,0.08)", text: "#C9A84C", border: "rgba(201,168,76,0.25)" },
  low:    { bg: "rgba(56,161,105,0.08)", text: "#38A169", border: "rgba(56,161,105,0.25)" },
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
        <h1 className="text-2xl font-bold tracking-tight" style={{ color: "#F5F5F5" }}>
          Mis Consultas
        </h1>
        <p className="text-sm mt-1" style={{ color: "#888888" }}>
          Seguimiento de las preguntas que han sido escaladas al equipo.
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

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 rounded-xl animate-pulse" style={{ backgroundColor: "#1A1A1A" }} />
          ))}
        </div>
      ) : tickets.length === 0 ? (
        <div
          className="card card-padding text-center"
        >
          <p className="text-sm" style={{ color: "#888888" }}>
            No tienes consultas escaladas.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {tickets.map((ticket) => {
            const cfg = statusConfig[ticket.status as keyof typeof statusConfig] ?? statusConfig.open;
            const Icon = cfg.icon;
            const pColor = priorityColors[ticket.priority] ?? priorityColors["medium"];
            const isResolved = ticket.status === "resolved";

            return (
              <div
                key={ticket.id}
                className="card card-padding space-y-3"
                style={isResolved ? { borderColor: "rgba(56,161,105,0.3)" } : {}}
              >
                {/* Title + meta */}
                <div className="flex items-start gap-3">
                  <Icon size={16} strokeWidth={1.75} style={{ color: cfg.color, marginTop: 2, flexShrink: 0 }} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium" style={{ color: "#F5F5F5" }}>
                      {ticket.question}
                    </p>
                    <div className="flex flex-wrap items-center gap-2 mt-1.5">
                      <span
                        className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border"
                        style={{ backgroundColor: pColor.bg, color: pColor.text, borderColor: pColor.border }}
                      >
                        {ticket.priority}
                      </span>
                      <span className="text-xs" style={{ color: cfg.color }}>
                        {cfg.label}
                      </span>
                      <span className="text-xs" style={{ color: "#555555" }}>
                        {new Date(ticket.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Resolution */}
                {isResolved && ticket.resolution_message && (
                  <div
                    className="rounded-lg border px-3 py-3"
                    style={{
                      backgroundColor: "rgba(56,161,105,0.06)",
                      borderColor: "rgba(56,161,105,0.2)",
                    }}
                  >
                    <p className="text-xs font-semibold mb-1.5" style={{ color: "#38A169" }}>
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
