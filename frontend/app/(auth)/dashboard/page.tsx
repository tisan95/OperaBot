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
} from "lucide-react";

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
        <p className="text-xs font-medium uppercase tracking-widest" style={{ color: "#888888" }}>
          {title}
        </p>
        <p className="text-3xl font-bold mt-2" style={{ color: "#F5F5F5" }}>
          {value}
        </p>
        {subtitle && (
          <p className="text-xs mt-1" style={{ color: "#555555" }}>
            {subtitle}
          </p>
        )}
      </div>
      <Icon size={18} strokeWidth={1.5} style={{ color: "#C9A84C" }} />
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
    <div
      className="flex items-center justify-between p-3 rounded-lg border"
      style={{ backgroundColor: "#111111", borderColor: "#2A2A2A" }}
    >
      <div>
        <p className="text-sm font-medium" style={{ color: "#F5F5F5" }}>
          {service}
        </p>
        <p className="text-xs mt-0.5" style={{ color: "#555555" }}>
          {message}
        </p>
      </div>
      <span className={isHealthy ? "badge-success" : "badge-error"}>
        {isHealthy ? "Healthy" : "Unavailable"}
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
        <h1 className="text-3xl font-bold tracking-tight" style={{ color: "#F5F5F5" }}>
          Bienvenido, {user?.email?.split("@")[0]}
        </h1>
        <div className="flex items-center gap-3 mt-2 flex-wrap">
          <p className="text-sm" style={{ color: "#888888" }}>
            {company?.name} · Operational Knowledge Assistant
          </p>
          {isSuperAdmin && <span className="badge-primary">Super Admin</span>}
          {user?.role === "admin" && <span className="badge-primary">Admin</span>}
        </div>
      </div>

      {/* System Stats — solo super_admin */}
      {isSuperAdmin && (
        <>
          {error && (
            <div
              className="px-4 py-3 rounded-lg border text-sm"
              style={{
                backgroundColor: "rgba(229,62,62,0.08)",
                borderColor: "rgba(229,62,62,0.3)",
                color: "#E53E3E",
              }}
            >
              Error cargando analytics: {error}
            </div>
          )}

          {loading ? (
            <div className="space-y-4">
              <div className="h-28 rounded-xl animate-pulse" style={{ backgroundColor: "#1A1A1A" }} />
              <div className="h-28 rounded-xl animate-pulse" style={{ backgroundColor: "#1A1A1A" }} />
            </div>
          ) : stats ? (
            <>
              <section>
                <h2
                  className="text-xs font-semibold uppercase tracking-widest mb-4"
                  style={{ color: "#555555" }}
                >
                  Knowledge Base
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <MetricCard
                    icon={FileText}
                    title="Documents"
                    value={stats.documents.total_documents}
                    subtitle={`${stats.documents.total_vectors} vectors`}
                  />
                  <MetricCard
                    icon={BookOpen}
                    title="FAQs"
                    value={stats.faqs.total_faqs}
                    subtitle={`${stats.faqs.total_vectors} vectors`}
                  />
                  <MetricCard
                    icon={HardDrive}
                    title="Storage"
                    value={`${(stats.documents.total_size_bytes / 1024).toFixed(1)} KB`}
                    subtitle="Total docs"
                  />
                  <MetricCard
                    icon={TrendingUp}
                    title="Processed Today"
                    value={stats.documents.documents_processed_today}
                    subtitle="new documents"
                  />
                </div>
              </section>

              <section>
                <h2
                  className="text-xs font-semibold uppercase tracking-widest mb-4"
                  style={{ color: "#555555" }}
                >
                  Chat Analytics (hoy)
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
                    title="Success Rate"
                    value={`${(stats.chat_today.success_rate * 100).toFixed(1)}%`}
                    subtitle="respuestas RAG"
                  />
                  <MetricCard
                    icon={Target}
                    title="Confidence"
                    value={`${(stats.chat_today.avg_confidence * 100).toFixed(0)}%`}
                    subtitle="score promedio"
                  />
                </div>
              </section>

              <section>
                <h2
                  className="text-xs font-semibold uppercase tracking-widest mb-4"
                  style={{ color: "#555555" }}
                >
                  System Services
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {stats.services.map((service) => (
                    <ServiceStatus key={service.service} {...service} />
                  ))}
                </div>
              </section>

              <p className="text-xs text-center" style={{ color: "#555555" }}>
                Última actualización: {new Date(stats.timestamp).toLocaleTimeString()}
              </p>
            </>
          ) : null}
        </>
      )}

      {/* Quick Actions */}
      <section>
        <h2
          className="text-xs font-semibold uppercase tracking-widest mb-4"
          style={{ color: "#555555" }}
        >
          Quick Actions
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            href="/chat"
            className="group card card-padding flex items-center justify-between transition-all duration-200"
            style={{ borderColor: "#2A2A2A" }}
            onMouseEnter={(e) =>
              ((e.currentTarget as HTMLAnchorElement).style.borderColor = "#C9A84C")
            }
            onMouseLeave={(e) =>
              ((e.currentTarget as HTMLAnchorElement).style.borderColor = "#2A2A2A")
            }
          >
            <div>
              <div className="flex items-center gap-2 mb-1">
                <MessageSquare size={15} strokeWidth={1.5} style={{ color: "#C9A84C" }} />
                <h3 className="font-semibold text-sm" style={{ color: "#F5F5F5" }}>
                  Iniciar Chat
                </h3>
              </div>
              <p className="text-xs" style={{ color: "#888888" }}>
                Consulta sobre tu base de conocimiento
              </p>
            </div>
            <ArrowRight size={15} strokeWidth={1.5} style={{ color: "#555555" }} />
          </Link>

          <Link
            href="/faq"
            className="group card card-padding flex items-center justify-between transition-all duration-200"
            style={{ borderColor: "#2A2A2A" }}
            onMouseEnter={(e) =>
              ((e.currentTarget as HTMLAnchorElement).style.borderColor = "#C9A84C")
            }
            onMouseLeave={(e) =>
              ((e.currentTarget as HTMLAnchorElement).style.borderColor = "#2A2A2A")
            }
          >
            <div>
              <div className="flex items-center gap-2 mb-1">
                <BookOpen size={15} strokeWidth={1.5} style={{ color: "#C9A84C" }} />
                <h3 className="font-semibold text-sm" style={{ color: "#F5F5F5" }}>
                  Ver FAQs
                </h3>
              </div>
              <p className="text-xs" style={{ color: "#888888" }}>
                Explora la base de conocimiento
              </p>
            </div>
            <ArrowRight size={15} strokeWidth={1.5} style={{ color: "#555555" }} />
          </Link>

          {isAdmin && (
            <Link
              href="/documents"
              className="group card card-padding flex items-center justify-between transition-all duration-200"
              style={{ borderColor: "#2A2A2A" }}
              onMouseEnter={(e) =>
                ((e.currentTarget as HTMLAnchorElement).style.borderColor = "#C9A84C")
              }
              onMouseLeave={(e) =>
                ((e.currentTarget as HTMLAnchorElement).style.borderColor = "#2A2A2A")
              }
            >
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <FileText size={15} strokeWidth={1.5} style={{ color: "#C9A84C" }} />
                  <h3 className="font-semibold text-sm" style={{ color: "#F5F5F5" }}>
                    Subir Documentos
                  </h3>
                </div>
                <p className="text-xs" style={{ color: "#888888" }}>
                  Gestiona la base de conocimiento
                </p>
              </div>
              <ArrowRight size={15} strokeWidth={1.5} style={{ color: "#555555" }} />
            </Link>
          )}
        </div>
      </section>
    </div>
  );
}
