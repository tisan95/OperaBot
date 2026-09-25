"use client";

import { useAuthContext } from "@/components/Auth/AuthProvider";
import { apiFetch } from "@/lib/api";
import Link from "next/link";
import { useEffect, useState } from "react";
import {
  FileText,
  BookOpen,
  HardDrive,
  TrendingUp,
  MessageSquare,
  CheckCircle,
  Target,
  ArrowRight,
  Clock,
  CircleCheck,
  AlertCircle,
} from "lucide-react";
import { Ticket } from "@/lib/types";
import { sanitizeHtml } from "@/lib/sanitize";

interface SystemStats {
  documents: {
    total_documents: number;
    total_vectors: number;
    total_size_bytes: number;
    documents_processed_today: number;
  };
  faqs: {
    total_faqs: number;
    total_vectors: number;
    last_updated: string | null;
  };
  chat_today: {
    total_chats_today: number;
    success_rate: number;
    avg_response_time_ms: number;
    avg_confidence: number;
  };
  services: Array<{
    service: string;
    status: string;
    message: string;
  }>;
  performance: {
    avg_response_time_ms: number;
    avg_confidence: number;
    vectors_created_today: number;
    docs_processed_today: number;
  };
  timestamp: string;
}

interface MetricCardProps {
  icon: React.ElementType;
  title: string;
  value: string | number;
  subtitle?: string;
}

const MetricCard = ({ icon: Icon, title, value, subtitle }: MetricCardProps) => (
  <div className="card card-padding">
    <div className="flex items-start justify-between">
      <div>
        <p className="text-xs font-medium uppercase tracking-widest text-text-secondary">
          {title}
        </p>
        <p className="text-3xl font-bold mt-2 text-text-primary">
          {value}
        </p>
        {subtitle && (
          <p className="text-xs mt-1 text-muted">
            {subtitle}
          </p>
        )}
      </div>
      <Icon size={18} strokeWidth={1.5} className="text-gold" />
    </div>
  </div>
);

const ServiceStatus = ({
  service,
  status,
  message,
}: {
  service: string;
  status: string;
  message: string;
}) => {
  const isHealthy = status === "healthy";
  return (
    <div className="flex items-center justify-between p-3 rounded-lg border bg-surface border-border">
      <div>
        <p className="text-sm font-medium text-text-primary">
          {service}
        </p>
        <p className="text-xs mt-0.5 text-muted">
          {message}
        </p>
      </div>
      <span className={isHealthy ? "badge-success" : "badge-error"}>
        {isHealthy ? "Activo" : "No disponible"}
      </span>
    </div>
  );
};

export default function DashboardPage() {
  const { user, company } = useAuthContext();
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isAdmin = user?.role === "admin" || user?.role === "super_admin";
  const isSuperAdmin = user?.role === "super_admin";
  const isUser = user?.role === "user";

  const [myTickets, setMyTickets] = useState<Ticket[]>([]);

  useEffect(() => {
    if (!isUser) return;
    apiFetch("/tickets/my")
      .then((data) => setMyTickets(Array.isArray(data) ? data : []))
      .catch(() => {});
  }, [isUser]);

  useEffect(() => {
    if (!isSuperAdmin) {
      setLoading(false);
      return;
    }

    const loadStats = async () => {
      try {
        const data = await apiFetch("/admin/system-stats");
        setStats(data);
      } catch (err: any) {
        console.error("Failed to load system stats:", err);
        setError(err.message || "Failed to load analytics");
      } finally {
        setLoading(false);
      }
    };

    loadStats();
    const interval = setInterval(loadStats, 30000);

    return () => clearInterval(interval);
  }, [isSuperAdmin]);

  return (
    <div className="space-y-8">
      {/* Welcome */}
      <div className="animate-slideUp">
        <h1 className="text-3xl font-bold tracking-tight text-text-primary">
          Bienvenido, {user?.email?.split("@")[0]}
        </h1>
        <div className="flex items-center gap-3 mt-2 flex-wrap">
          <p className="text-sm text-text-secondary">
            {company?.name} · Asistente de Conocimiento Operacional
          </p>
          {isSuperAdmin && <span className="badge-primary">Super Admin</span>}
          {user?.role === "admin" && <span className="badge-primary">Admin</span>}
        </div>
      </div>

      {/* System Stats — solo super_admin */}
      {isSuperAdmin && (
        <>
          {error && (
            <div className="px-4 py-3 rounded-lg border text-sm bg-error/8 border-error/30 text-error">
              Error cargando analytics: {error}
            </div>
          )}

          {loading ? (
            <div className="space-y-4">
              <div className="h-28 rounded-xl animate-pulse bg-card" />
              <div className="h-28 rounded-xl animate-pulse bg-card" />
            </div>
          ) : stats ? (
            <>
              <section>
                <h2 className="text-xs font-semibold uppercase tracking-widest mb-4 text-muted">
                  Base de Conocimiento
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <MetricCard
                    icon={FileText}
                    title="Documentos"
                    value={stats.documents.total_documents}
                    subtitle={`${stats.documents.total_vectors} vectores`}
                  />
                  <MetricCard
                    icon={BookOpen}
                    title="FAQs"
                    value={stats.faqs.total_faqs}
                    subtitle={`${stats.faqs.total_vectors} vectores`}
                  />
                  <MetricCard
                    icon={HardDrive}
                    title="Almacenamiento"
                    value={`${(stats.documents.total_size_bytes / 1024).toFixed(1)} KB`}
                    subtitle="Total documentos"
                  />
                  <MetricCard
                    icon={TrendingUp}
                    title="Procesados Hoy"
                    value={stats.documents.documents_processed_today}
                    subtitle="nuevos documentos"
                  />
                </div>
              </section>

              <section>
                <h2 className="text-xs font-semibold uppercase tracking-widest mb-4 text-muted">
                  Analíticas del Chat (hoy)
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <MetricCard
                    icon={MessageSquare}
                    title="Mensajes"
                    value={stats.chat_today.total_chats_today}
                    subtitle="conversaciones hoy"
                  />
                  <MetricCard
                    icon={CheckCircle}
                    title="Tasa de Éxito"
                    value={`${(stats.chat_today.success_rate * 100).toFixed(1)}%`}
                    subtitle="respuestas RAG"
                  />
                  <MetricCard
                    icon={Target}
                    title="Precisión"
                    value={`${(stats.chat_today.avg_confidence * 100).toFixed(0)}%`}
                    subtitle="score promedio"
                  />
                </div>
              </section>

              <section>
                <h2 className="text-xs font-semibold uppercase tracking-widest mb-4 text-muted">
                  Estado del Sistema
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {stats.services.map((service) => (
                    <ServiceStatus key={service.service} {...service} />
                  ))}
                </div>
              </section>

              <p className="text-xs text-center text-muted">
                Última actualización: {new Date(stats.timestamp).toLocaleTimeString()}
              </p>
            </>
          ) : null}
        </>
      )}

      {/* Mis consultas escaladas — solo user con tickets */}
      {isUser && myTickets.length > 0 && (
        <section>
          <h2 className="text-xs font-semibold uppercase tracking-widest mb-4 text-muted">
            Mis consultas escaladas
          </h2>
          <div className="space-y-3">
            {myTickets.map((ticket) => {
              const isResolved = ticket.status === "resolved";
              const isPending = ticket.status === "open";
              return (
                <div
                  key={ticket.id}
                  className={`card card-padding space-y-2 ${isResolved ? "border-success/30" : ""}`}
                >
                  <div className="flex items-start gap-3">
                    <div className="shrink-0 mt-0.5">
                      {isResolved ? (
                        <CircleCheck size={15} strokeWidth={1.5} className="text-success" />
                      ) : isPending ? (
                        <AlertCircle size={15} strokeWidth={1.5} className="text-gold" />
                      ) : (
                        <Clock size={15} strokeWidth={1.5} className="text-text-secondary" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-text-primary">
                        {ticket.question}
                      </p>
                      <p className="text-xs mt-0.5 text-muted">
                        {isResolved ? "Resuelto" : isPending ? "Pendiente" : "En revisión"} ·{" "}
                        {new Date(ticket.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  {isResolved && ticket.resolution_message && (
                    <div className="rounded-lg border px-3 py-2 bg-success/6 border-success/20">
                      <p className="text-xs font-semibold mb-1 text-success">
                        Respuesta del equipo
                      </p>
                      <div
                        className="rich-content text-sm"
                        dangerouslySetInnerHTML={{ __html: sanitizeHtml(ticket.resolution_message ?? "") }}
                      />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Quick Actions */}
      <section>
        <h2 className="text-xs font-semibold uppercase tracking-widest mb-4 text-muted">
          Acciones Rápidas
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            href="/chat"
            className="group card card-padding flex items-center justify-between transition-all duration-200 hover:border-gold"
          >
            <div>
              <div className="flex items-center gap-2 mb-1">
                <MessageSquare size={15} strokeWidth={1.5} className="text-gold" />
                <h3 className="font-semibold text-sm text-text-primary">
                  Iniciar Chat
                </h3>
              </div>
              <p className="text-xs text-text-secondary">
                Consulta sobre tu base de conocimiento
              </p>
            </div>
            <ArrowRight size={15} strokeWidth={1.5} className="text-muted" />
          </Link>

          <Link
            href="/faq"
            className="group card card-padding flex items-center justify-between transition-all duration-200 hover:border-gold"
          >
            <div>
              <div className="flex items-center gap-2 mb-1">
                <BookOpen size={15} strokeWidth={1.5} className="text-gold" />
                <h3 className="font-semibold text-sm text-text-primary">
                  Ver FAQs
                </h3>
              </div>
              <p className="text-xs text-text-secondary">
                Explora la base de conocimiento
              </p>
            </div>
            <ArrowRight size={15} strokeWidth={1.5} className="text-muted" />
          </Link>

          {isAdmin && (
            <Link
              href="/documents"
              className="group card card-padding flex items-center justify-between transition-all duration-200 hover:border-gold"
            >
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <FileText size={15} strokeWidth={1.5} className="text-gold" />
                  <h3 className="font-semibold text-sm text-text-primary">
                    Subir Documentos
                  </h3>
                </div>
                <p className="text-xs text-text-secondary">
                  Gestiona la base de conocimiento
                </p>
              </div>
              <ArrowRight size={15} strokeWidth={1.5} className="text-muted" />
            </Link>
          )}
        </div>
      </section>
    </div>
  );
}
