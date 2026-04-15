"use client";

import { useAuthContext } from "@/components/Auth/AuthProvider";
import { useRouter } from "next/navigation";

export default function AdminPage() {
  const { user } = useAuthContext();
  const router = useRouter();

  if (user?.role !== "admin") {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h1 className="text-2xl font-bold text-yellow-900">Access Denied</h1>
        <p className="text-yellow-800 mt-2">
          You do not have permission to access the admin panel.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-4xl font-bold text-gray-900">Admin Panel</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900">Knowledge Base</h3>
          <p className="text-gray-600 mt-2">Manage FAQ articles and documents</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900">Analytics</h3>
          <p className="text-gray-600 mt-2">View usage and performance metrics</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900">Kanban</h3>
          <p className="text-gray-600 mt-2">Create tasks in external tools</p>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <p className="text-blue-800 text-sm">
          Admin features coming soon in FEATURE-002, FEATURE-003, and beyond.
        </p>
      </div>
    </div>
  );
}
