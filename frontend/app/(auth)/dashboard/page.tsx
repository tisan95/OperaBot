"use client";

import { useAuthContext } from "@/components/Auth/AuthProvider";
import { apiFetch } from "@/lib/api";
import Link from "next/link";
import { useEffect, useState } from "react";

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
  icon: string;
  title: string;
  value: string | number;
  subtitle?: string;
  color: "indigo" | "cyan" | "green" | "orange" | "red";
}

const MetricCard = ({ icon, title, value, subtitle, color }: MetricCardProps) => {
  const colorClasses = {
    indigo: "from-indigo-50 to-blue-50 border-indigo-100",
    cyan: "from-cyan-50 to-blue-50 border-cyan-100",
    green: "from-green-50 to-emerald-50 border-green-100",
    orange: "from-orange-50 to-amber-50 border-orange-100",
    red: "from-red-50 to-pink-50 border-red-100",
  };

  return (
    <div className={`card card-padding bg-gradient-to-br ${colorClasses[color]} border`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-600">{title}</p>
          <p className="text-3xl font-bold text-slate-900 mt-2">{value}</p>
          {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
        </div>
        <div className="text-4xl">{icon}</div>
      </div>
    </div>
  );
};

const ServiceStatus = ({ service, status, message }: { service: string; status: string; message: string }) => {
  const statusColor = status === "healthy" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800";
  const statusIcon = status === "healthy" ? "✅" : "⚠️";

  return (
    <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-200">
      <div>
        <p className="font-semibold text-slate-900">{service}</p>
        <p className="text-xs text-slate-500">{message}</p>
      </div>
      <span className={`px-3 py-1 rounded-full text-sm font-semibold flex items-center gap-2 ${statusColor}`}>
        {statusIcon} {status === "healthy" ? "Healthy" : "Unavailable"}
      </span>
    </div>
  );
};

export default function DashboardPage() {
  const { user, company } = useAuthContext();
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user?.role !== "admin") {
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
    const interval = setInterval(loadStats, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, [user?.role]);

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="animate-slideUp">
        <h1 className="text-4xl font-bold text-slate-900 tracking-tight">
          Welcome back, {user?.email?.split("@")[0]}!
        </h1>
        <p className="text-lg text-slate-600 mt-3">
          {company?.name} • Operational Knowledge Assistant
          {user?.role === "admin" && <span className="ml-3 text-sm bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full font-semibold">Admin</span>}
        </p>
      </div>

      {/* Admin Analytics Dashboard */}
      {user?.role === "admin" && (
        <>
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 font-semibold">Error loading analytics: {error}</p>
            </div>
          )}

          {loading ? (
            <div className="space-y-4">
              <div className="h-32 bg-slate-100 rounded-lg animate-pulse"></div>
              <div className="h-32 bg-slate-100 rounded-lg animate-pulse"></div>
            </div>
          ) : stats ? (
            <>
              {/* Knowledge Base Metrics */}
              <section>
                <h2 className="text-2xl font-bold text-slate-900 mb-4">📚 Knowledge Base</h2>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <MetricCard
                    icon="📄"
                    title="Documents"
                    value={stats.documents.total_documents}
                    subtitle={`${stats.documents.total_vectors} vectors`}
                    color="indigo"
                  />
                  <MetricCard
                    icon="📋"
                    title="FAQs"
                    value={stats.faqs.total_faqs}
                    subtitle={`${stats.faqs.total_vectors} vectors`}
                    color="cyan"
                  />
                  <MetricCard
                    icon="💾"
                    title="Storage"
                    value={`${(stats.documents.total_size_bytes / 1024).toFixed(1)} KB`}
                    subtitle="Total documents"
                    color="green"
                  />
                  <MetricCard
                    icon="📈"
                    title="Processed Today"
                    value={stats.documents.documents_processed_today}
                    subtitle="new documents"
                    color="orange"
                  />
                </div>
              </section>

              {/* Chat Metrics */}
              <section>
                <h2 className="text-2xl font-bold text-slate-900 mb-4">💬 Chat Analytics (Today)</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <MetricCard
                    icon="💭"
                    title="Messages"
                    value={stats.chat_today.total_chats_today}
                    subtitle="conversations today"
                    color="indigo"
                  />
                  <MetricCard
                    icon="✨"
                    title="Success Rate"
                    value={`${(stats.chat_today.success_rate * 100).toFixed(1)}%`}
                    subtitle="RAG responses"
                    color={stats.chat_today.success_rate >= 0.8 ? "green" : "orange"}
                  />
                  <MetricCard
                    icon="🎯"
                    title="Confidence"
                    value={`${(stats.chat_today.avg_confidence * 100).toFixed(0)}%`}
                    subtitle="average score"
                    color={stats.chat_today.avg_confidence >= 0.7 ? "green" : "orange"}
                  />
                </div>
              </section>

              {/* Services Status */}
              <section>
                <h2 className="text-2xl font-bold text-slate-900 mb-4">🔧 System Services</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {stats.services.map((service) => (
                    <ServiceStatus key={service.service} {...service} />
                  ))}
                </div>
              </section>

              {/* Last Updated */}
              <p className="text-xs text-slate-400 text-center">
                Last updated: {new Date(stats.timestamp).toLocaleTimeString()}
              </p>
            </>
          ) : null}
        </>
      )}

      {/* Quick Actions */}
      <section>
        <h2 className="text-2xl font-bold text-slate-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link href="/chat" className="group relative overflow-hidden card bg-gradient-to-br from-indigo-600 to-blue-600 text-white p-6 hover:shadow-xl transition">
            <div className="relative z-10">
              <h3 className="font-semibold text-lg mb-2">💬 Start Chat</h3>
              <p className="text-sm text-indigo-100">Ask questions about your operations</p>
            </div>
            <div className="absolute right-0 top-0 text-6xl opacity-10">→</div>
          </Link>

          <Link href="/faq" className="group relative overflow-hidden card bg-gradient-to-br from-slate-700 to-slate-900 text-white p-6 hover:shadow-xl transition">
            <div className="relative z-10">
              <h3 className="font-semibold text-lg mb-2">📚 Browse FAQ</h3>
              <p className="text-sm text-slate-300">Explore knowledge base</p>
            </div>
            <div className="absolute right-0 top-0 text-6xl opacity-10">→</div>
          </Link>

          {user?.role === "admin" && (
            <Link href="/documents" className="group relative overflow-hidden card bg-gradient-to-br from-emerald-600 to-teal-600 text-white p-6 hover:shadow-xl transition">
              <div className="relative z-10">
                <h3 className="font-semibold text-lg mb-2">📤 Upload Documents</h3>
                <p className="text-sm text-emerald-100">Manage knowledge base</p>
              </div>
              <div className="absolute right-0 top-0 text-6xl opacity-10">→</div>
            </Link>
          )}
        </div>
      </section>

      {/* System Status Banner */}
      {user?.role !== "admin" && (
        <div className="card card-padding bg-gradient-to-r from-indigo-50 to-blue-50 border border-indigo-100">
          <h3 className="font-bold text-slate-900 mb-4 flex items-center gap-2">
            <span className="text-xl">✨</span> Powered by Local AI
          </h3>
          <ul className="space-y-2 text-sm text-slate-700">
            <li className="flex items-start gap-3">
              <span className="text-indigo-600 font-bold mt-0.5">✓</span>
              <span>100% local inference (Ollama)</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-indigo-600 font-bold mt-0.5">✓</span>
              <span>Vector search with Qdrant</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-indigo-600 font-bold mt-0.5">✓</span>
              <span>Document-enhanced RAG responses</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-indigo-600 font-bold mt-0.5">✓</span>
              <span>Secure multi-tenant architecture</span>
            </li>
          </ul>
        </div>
      )}
    </div>
  );
}
