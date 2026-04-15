"use client";

import { useAuthContext } from "@/components/Auth/AuthProvider";
import Link from "next/link";

export default function DashboardPage() {
  const { user, company } = useAuthContext();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold text-gray-900">
          Welcome, {user?.email}!
        </h1>
        <p className="text-lg text-gray-600 mt-2">
          {company?.name}
        </p>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Quick Start
        </h2>

        <p className="text-gray-600 mb-6">
          Welcome to OperaBot! Here's what you can do:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition">
            <h3 className="font-semibold text-gray-900 mb-2">📚 Browse FAQ</h3>
            <p className="text-sm text-gray-600">
              Explore operational knowledge and FAQs
            </p>
          </div>

          <div className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition">
            <h3 className="font-semibold text-gray-900 mb-2">💬 Chat with AI</h3>
            <p className="text-sm text-gray-600">
              Ask operational questions and get answers
            </p>
          </div>

          {user?.role === "admin" && (
            <>
              <div className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition">
                <h3 className="font-semibold text-gray-900 mb-2">⚙️ Admin Panel</h3>
                <p className="text-sm text-gray-600">
                  Manage knowledge and view analytics
                </p>
              </div>

              <div className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition">
                <h3 className="font-semibold text-gray-900 mb-2">📊 Analytics</h3>
                <p className="text-sm text-gray-600">
                  View usage patterns and insights
                </p>
              </div>
            </>
          )}
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-2">ℹ️ Next Steps</h3>
        <p className="text-blue-800 text-sm">
          FEATURE-001 (User Authentication & Login) is now complete! 🎉
        </p>
        <p className="text-blue-800 text-sm mt-2">
          Next feature coming soon: FAQ Browser, Chat Interface, and Admin Panel
        </p>
      </div>
    </div>
  );
}
