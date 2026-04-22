"use client";

import { apiFetch } from "@/lib/api";
import { useEffect, useState } from "react";
// Importamos el contexto y el enrutador para la seguridad
import { useAuthContext } from "@/components/Auth/AuthProvider";
import { useRouter } from "next/navigation";

export default function UsersPage() {
  // Extraemos el usuario actual y la función para redirigir
  const { user } = useAuthContext();
  const router = useRouter();

  const [users, setUsers] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // Estados para el Modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [error, setError] = useState("");
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    role: "user"
  });

  // EFECTO DE SEGURIDAD: Si está logueado pero NO es admin, lo echamos
  useEffect(() => {
    if (user && user.role !== "admin") {
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

  // Función para CREAR usuario
  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await apiFetch("/users/", {
        method: "POST",
        body: JSON.stringify(formData),
      });
      // Si va bien: cerramos modal, limpiamos formulario y recargamos tabla
      setIsModalOpen(false);
      setFormData({ email: "", password: "", role: "user" });
      loadUsers();
    } catch (err: any) {
      setError(err.message || "Error al crear el usuario. Revisa los datos.");
    }
  };

  // Función para ELIMINAR usuario
  const handleDeleteUser = async (id: string) => {
    if (!window.confirm("¿Estás seguro de que quieres eliminar este usuario permanentemente?")) return;
    
    try {
      await apiFetch(`/users/${id}`, { method: "DELETE" });
      loadUsers(); // Recargamos la tabla
    } catch (err: any) {
      alert(err.message || "Error al eliminar el usuario");
    }
  };

  // Si no es admin, devolvemos null temporalmente para que no haya un "destello" visual antes de la redirección
  if (user && user.role !== "admin") return null;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-slate-800">Gestión de Usuarios</h1>
        <button 
          onClick={() => setIsModalOpen(true)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition"
        >
          + Nuevo Usuario
        </button>
      </div>

      <div className="bg-white rounded-lg shadow border border-slate-200">
        <table className="w-full text-left">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-6 py-4 font-semibold text-slate-600">Email</th>
              <th className="px-6 py-4 font-semibold text-slate-600">Rol</th>
              <th className="px-6 py-4 font-semibold text-slate-600">Estado</th>
              <th className="px-6 py-4 font-semibold text-slate-600">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr><td colSpan={4} className="p-6 text-center">Cargando...</td></tr>
            ) : (
              users.map((u: any) => (
                <tr key={u.id} className="border-b border-slate-100 hover:bg-slate-50">
                  <td className="px-6 py-4">{u.email}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs uppercase font-bold ${u.role === 'admin' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'}`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    {u.is_active ? "✅ Activo" : "❌ Inactivo"}
                  </td>
                  <td className="px-6 py-4">
                    <button 
                      onClick={() => handleDeleteUser(u.id)}
                      className="text-red-500 hover:text-red-700 transition"
                      title="Eliminar usuario"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* MODAL EMERGENTE PARA CREAR USUARIO */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-8 w-full max-w-md shadow-2xl">
            <h2 className="text-xl font-bold mb-4">Crear Nuevo Usuario</h2>
            
            {error && <div className="bg-red-100 text-red-700 p-3 rounded mb-4 text-sm">{error}</div>}
            
            <form onSubmit={handleCreateUser} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
                <input 
                  type="email" required
                  className="w-full border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Contraseña (mín 6 char)</label>
                <input 
                  type="password" required minLength={6}
                  className="w-full border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Rol</label>
                <select 
                  className="w-full border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none"
                  value={formData.role}
                  onChange={(e) => setFormData({...formData, role: e.target.value})}
                >
                  <option value="user">Usuario normal</option>
                  <option value="admin">Administrador</option>
                </select>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button 
                  type="button" 
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg transition"
                >
                  Cancelar
                </button>
                <button 
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
                >
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