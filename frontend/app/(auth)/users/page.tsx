"use client";

import { apiFetch } from "@/lib/api";
import { useEffect, useState } from "react";
import { useAuthContext } from "@/components/Auth/AuthProvider";
import { useRouter } from "next/navigation";
import { Trash2, X } from "lucide-react";

export default function UsersPage() {
  const { user } = useAuthContext();
  const router = useRouter();

  const [users, setUsers] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [pendingRoles, setPendingRoles] = useState<Record<string, string>>({});

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [error, setError] = useState("");
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    role: "user",
  });

  useEffect(() => {
    if (user && user.role !== "super_admin") {
      router.push("/dashboard");
    }
  }, [user, router]);

  const loadUsers = async () => {
    try {
      const data = await apiFetch("/users/");
      if (data) setUsers(data);
    } catch (error) {
      console.error("Error cargando usuarios:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await apiFetch("/users/", {
        method: "POST",
        body: JSON.stringify(formData),
      });
      setIsModalOpen(false);
      setFormData({ email: "", password: "", role: "user" });
      loadUsers();
    } catch (err: any) {
      setError(err.message || "Error al crear el usuario. Revisa los datos.");
    }
  };

  const handleDeleteUser = async (id: string) => {
    if (!window.confirm("¿Estás seguro de que quieres eliminar este usuario permanentemente?"))
      return;

    try {
      await apiFetch(`/users/${id}`, { method: "DELETE" });
      loadUsers();
    } catch (err: any) {
      alert(err.message || "Error al eliminar el usuario");
    }
  };

  const handleRoleChange = (userId: string, role: string) => {
    setPendingRoles((current) => ({ ...current, [userId]: role }));
  };

  const handleApproveUser = async (id: string) => {
    const role = pendingRoles[id] || "user";

    try {
      await apiFetch(`/users/${id}/approve`, {
        method: "PATCH",
        body: JSON.stringify({ role }),
      });
      loadUsers();
    } catch (err: any) {
      alert(err.message || "Error al aprobar el usuario");
    }
  };

  if (user && user.role !== "super_admin") return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" style={{ color: "#F5F5F5" }}>
            Gestión de Usuarios
          </h1>
          <p className="text-sm mt-1" style={{ color: "#888888" }}>
            Aprueba, gestiona y elimina usuarios.
          </p>
        </div>
        <button onClick={() => setIsModalOpen(true)} className="btn btn-primary">
          + Nuevo Usuario
        </button>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead style={{ borderBottom: "1px solid #2A2A2A" }}>
            <tr>
              {["Email", "Rol", "Estado", "Acciones"].map((col) => (
                <th
                  key={col}
                  className="px-6 py-4 text-left text-xs font-medium uppercase tracking-wider"
                  style={{ color: "#888888", backgroundColor: "#111111" }}
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td
                  colSpan={4}
                  className="px-6 py-6 text-center text-sm"
                  style={{ color: "#888888" }}
                >
                  Cargando...
                </td>
              </tr>
            ) : (
              users.map((u: any) => (
                <tr
                  key={u.id}
                  style={{ borderBottom: "1px solid #2A2A2A", transition: "background 0.1s" }}
                  onMouseEnter={(e) =>
                    ((e.currentTarget as HTMLTableRowElement).style.backgroundColor = "#1E1E1E")
                  }
                  onMouseLeave={(e) =>
                    ((e.currentTarget as HTMLTableRowElement).style.backgroundColor = "transparent")
                  }
                >
                  <td className="px-6 py-4" style={{ color: "#F5F5F5" }}>
                    {u.email}
                  </td>
                  <td className="px-6 py-4">
                    <span className="badge-primary">{u.role}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={u.status === "active" ? "badge-success" : "badge-warning"}
                    >
                      {u.status || "pendiente"}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    {u.status === "pending" ? (
                      <div className="space-y-2 max-w-[180px]">
                        <select
                          value={pendingRoles[u.id] || u.role || "user"}
                          onChange={(e) => handleRoleChange(u.id, e.target.value)}
                          className="input text-xs py-1.5"
                        >
                          <option value="user">Usuario</option>
                          <option value="admin">Administrador</option>
                        </select>
                        <button
                          onClick={() => handleApproveUser(u.id)}
                          className="btn btn-primary btn-sm w-full"
                        >
                          Aprobar
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => handleDeleteUser(u.id)}
                        className="btn btn-danger btn-sm px-2 py-1"
                        title="Eliminar usuario"
                      >
                        <Trash2 size={13} strokeWidth={1.75} />
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 flex items-center justify-center z-50" style={{ backgroundColor: "rgba(0,0,0,0.7)" }}>
          <div className="card card-padding w-full max-w-md rounded-2xl relative">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="absolute top-4 right-4 btn-ghost p-1"
            >
              <X size={16} strokeWidth={1.75} />
            </button>

            <h2 className="text-base font-semibold mb-5" style={{ color: "#F5F5F5" }}>
              Crear Nuevo Usuario
            </h2>

            {error && (
              <div
                className="px-4 py-3 rounded-lg border text-sm mb-4"
                style={{
                  backgroundColor: "rgba(229,62,62,0.08)",
                  borderColor: "rgba(229,62,62,0.3)",
                  color: "#E53E3E",
                }}
              >
                {error}
              </div>
            )}

            <form onSubmit={handleCreateUser} className="space-y-4">
              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "#888888" }}>
                  Email
                </label>
                <input
                  type="email"
                  required
                  className="input"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "#888888" }}>
                  Contraseña (mín 6 char)
                </label>
                <input
                  type="password"
                  required
                  minLength={6}
                  className="input"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "#888888" }}>
                  Rol
                </label>
                <select
                  className="input"
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                >
                  <option value="user">Usuario normal</option>
                  <option value="admin">Administrador</option>
                </select>
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="btn btn-secondary"
                >
                  Cancelar
                </button>
                <button type="submit" className="btn btn-primary">
                  Guardar Usuario
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
