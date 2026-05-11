"use client";
import { apiFetch } from "@/lib/api";
import { FormEvent, useEffect, useState } from "react";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  useEffect(() => { loadDocuments(); }, []);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const data = await apiFetch("/documents/");
      if (Array.isArray(data)) setDocuments(data);
    } catch (err) { console.error(err); } finally { setLoading(false); }
  };

  const handleUpload = async (e: FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;
    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      await apiFetch("/documents/upload", {
        method: "POST",
        body: formData,
      });

      setSelectedFile(null);
      loadDocuments();
      alert("Documento subido exitosamente");
    } catch (err: any) {
      console.error("Error capturado:", err);
      
      let mensajeFinal = "Error desconocido";
      
      if (err.detail) {
        mensajeFinal = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail);
      } else if (err.message) {
        mensajeFinal = err.message;
      } else {
        mensajeFinal = JSON.stringify(err);
      }

      setError(mensajeFinal);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId: string, filename: string) => {
    if (!window.confirm(`¿Eliminar "${filename}"? Esta acción no se puede deshacer.`)) {
      return;
    }

    setDeleting(docId);
    try {
      await apiFetch(`/documents/${docId}`, {
        method: "DELETE",
      });
      loadDocuments();
    } catch (err: any) {
      console.error("Error al eliminar:", err);
      let mensajeFinal = "Error desconocido";
      
      if (err.detail) {
        mensajeFinal = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail);
      } else if (err.message) {
        mensajeFinal = err.message;
      } else {
        mensajeFinal = JSON.stringify(err);
      }

      setError(mensajeFinal);
    } finally {
      setDeleting(null);
    }
  };

  return (
    <div className="p-8 space-y-6">
      <div className="bg-white p-8 rounded-xl border-2 border-slate-100 shadow-sm max-w-2xl">
        <h2 className="text-2xl font-bold mb-6 text-slate-800 flex items-center gap-2">
          <span>📤</span> Subir Documento
        </h2>
        
        <form onSubmit={handleUpload} className="space-y-4">
          <div className="group relative border-2 border-dashed border-slate-300 rounded-2xl p-12 text-center hover:border-indigo-500 hover:bg-indigo-50/30 transition-all cursor-pointer">
            <input 
              type="file" 
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" 
              accept=".pdf"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
            />
            <div className="space-y-3">
              <div className="text-5xl">📄</div>
              <p className="text-lg font-semibold text-slate-700">
                {selectedFile ? selectedFile.name : "Selecciona tu documento o manual (PDF)"}
              </p>
              <p className="text-sm text-slate-500 italic">Haz clic aquí para buscar el archivo</p>
            </div>
          </div>

          <button 
            disabled={!selectedFile || uploading} 
            className="w-full bg-indigo-600 text-white py-4 rounded-xl font-bold text-lg shadow-lg hover:bg-indigo-700 disabled:bg-slate-300 disabled:shadow-none transition-all active:scale-[0.98]"
          >
            {uploading ? "Procesando..." : "Subir Documento"}
          </button>
        </form>

        {error && (
          <div className="mt-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-r-lg">
            <p className="text-red-800 font-bold mb-1">Error:</p>
            <p className="text-red-700 font-mono text-xs break-all">{error}</p>
          </div>
        )}
      </div>

      <div className="bg-white p-6 rounded-xl border border-slate-100 shadow-sm">
        <h3 className="font-bold text-slate-700 mb-4">Documentos en el sistema:</h3>
        <div className="grid gap-2">
          {loading ? (
            <p className="text-slate-400 text-sm">Cargando documentos...</p>
          ) : documents.length === 0 ? (
            <p className="text-slate-400 text-sm italic">No hay documentos aún.</p>
          ) : (
            documents.map(doc => (
              <div key={doc.id} className="flex justify-between items-center p-3 bg-slate-50 rounded-lg border border-slate-200 text-sm group">
                <div className="flex-1">
                  <span className="font-medium block">{doc.filename}</span>
                  <span className="text-xs text-slate-500">{doc.file_size && `${(doc.file_size / 1024).toFixed(1)} KB`} • {doc.vector_count || 0} vectores</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                    doc.upload_status === 'completed' 
                      ? 'bg-green-100 text-green-700' 
                      : doc.upload_status === 'processing'
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {doc.upload_status}
                  </span>
                  <button
                    onClick={() => handleDelete(doc.id, doc.filename)}
                    disabled={deleting === doc.id}
                    className="px-2 py-1 text-red-600 hover:bg-red-50 rounded transition-colors disabled:opacity-50"
                    title="Eliminar documento"
                  >
                    {deleting === doc.id ? "..." : "🗑️"}
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}