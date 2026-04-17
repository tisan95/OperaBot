"use client";

import { useAuthContext } from "@/components/Auth/AuthProvider";
import Link from "next/link";

export default function DashboardPage() {
  const { user, company } = useAuthContext();

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="animate-slideUp">
        <h1 className="text-4xl font-bold text-slate-900 tracking-tight">
          Welcome back, {user?.email?.split('@')[0]}!
        </h1>
        <p className="text-lg text-slate-600 mt-3">
          {company?.name} • Operational Knowledge Assistant
        </p>
      </div>

      {/* Quick Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card card-padding bg-gradient-to-br from-indigo-50 to-blue-50 border border-indigo-100">
          <div className="text-3xl mb-3">💬</div>
          <h3 className="font-semibold text-slate-900">Chat Assistant</h3>
          <p className="text-sm text-slate-600 mt-2">Ask operational questions with AI</p>
        </div>

        <div className="card card-padding bg-gradient-to-br from-cyan-50 to-blue-50 border border-cyan-100">
          <div className="text-3xl mb-3">📚</div>
          <h3 className="font-semibold text-slate-900">FAQ Library</h3>
          <p className="text-sm text-slate-600 mt-2">Browse and manage knowledge base</p>
        </div>

        {user?.role === 'admin' && (
          <div className="card card-padding bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-100">
            <div className="text-3xl mb-3">📊</div>
            <h3 className="font-semibold text-slate-900">Admin Panel</h3>
            <p className="text-sm text-slate-600 mt-2">View analytics & manage settings</p>
          </div>
        )}
      </div>

      {/* Quick Links */}
      <div className="card card-padding">
        <h2 className="text-2xl font-bold text-slate-900 mb-6">Quick Actions</h2>

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
        </div>
      </div>

      {/* Info Banner */}
      <div className="card card-padding bg-gradient-to-r from-indigo-50 to-blue-50 border border-indigo-100">
        <h3 className="font-bold text-slate-900 mb-4 flex items-center gap-2">
          <span className="text-xl">✨</span> What's New
        </h3>
        <ul className="space-y-2 text-sm text-slate-700">
          <li className="flex items-start gap-3">
            <span className="text-indigo-600 font-bold mt-0.5">✓</span>
            <span>Secure authentication with JWT tokens</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-indigo-600 font-bold mt-0.5">✓</span>
            <span>Multi-tenant FAQ knowledge base</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-indigo-600 font-bold mt-0.5">✓</span>
            <span>AI-powered chat assistant with fallback</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-indigo-600 font-bold mt-0.5">✓</span>
            <span>Admin analytics dashboard</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
