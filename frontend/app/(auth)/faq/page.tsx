"use client";

import { apiFetch } from "@/lib/api";
import { FAQ } from "@/lib/types";
import { FormEvent, useEffect, useState } from "react";
import { useAuthContext } from "@/components/Auth/AuthProvider";
import RichEditor from "@/components/Shared/RichEditor";
import { sanitizeHtml } from "@/lib/sanitize";

export default function FAQPage() {
  const { user } = useAuthContext();
  const isAdmin = user?.role === "admin" || user?.role === "super_admin";

  const [faqs, setFaqs] = useState<FAQ[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [category, setCategory] = useState("");
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState<number | null>(null);
  const [editingFaqId, setEditingFaqId] = useState<number | null>(null);

  const loadFaqs = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await apiFetch("/faqs");
      setFaqs(data ?? []);
    } catch (err: any) {
      setError(err.message || "Failed to load FAQs");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFaqs();
  }, []);

  const handleEditClick = (faq: FAQ) => {
    setEditingFaqId(faq.id);
    setQuestion(faq.question);
    setAnswer(faq.answer);
    setCategory(faq.category ?? "");
    setError(null);
  };

  const handleDeleteClick = async (faqId: number, question: string) => {
    if (!window.confirm(`Delete FAQ: "${question}"? This action cannot be undone.`)) {
      return;
    }

    setDeleting(faqId);
    setError(null);

    try {
      await apiFetch(`/faqs/${faqId}`, { method: "DELETE" });
      setFaqs(faqs.filter((faq) => faq.id !== faqId));
      if (editingFaqId === faqId) {
        resetForm();
      }
    } catch (err: any) {
      setError(err.message || "Failed to delete FAQ");
    } finally {
      setDeleting(null);
    }
  };

  const resetForm = () => {
    setEditingFaqId(null);
    setQuestion("");
    setAnswer("");
    setCategory("");
    setError(null);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    if (!question.trim() || !answer.trim()) {
      setError("Question and answer are required.");
      return;
    }

    setSaving(true);

    try {
      if (editingFaqId) {
        await apiFetch(`/faqs/${editingFaqId}`, {
          method: "PUT",
          body: JSON.stringify({
            question: question.trim(),
            answer: answer.trim(),
            category: category.trim() || null,
          }),
        });
      } else {
        await apiFetch("/faqs", {
          method: "POST",
          body: JSON.stringify({
            question: question.trim(),
            answer: answer.trim(),
            category: category.trim() || null,
          }),
        });
      }

      resetForm();
      await loadFaqs();
    } catch (err: any) {
      setError(err.message || "Failed to save FAQ");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight" style={{ color: "#F5F5F5" }}>
          FAQs
        </h1>
        <p className="text-sm mt-1" style={{ color: "#888888" }}>
          Explora, añade y mantén el conocimiento operacional.
        </p>
      </div>

      <div className={`grid gap-6 ${isAdmin ? "lg:grid-cols-[1.6fr_1fr]" : "grid-cols-1"}`}>
        {/* Table */}
        <div className="card overflow-hidden">
          <div
            className="flex items-center justify-between border-b px-6 py-4"
            style={{ borderColor: "#2A2A2A" }}
          >
            <h2 className="text-sm font-semibold" style={{ color: "#F5F5F5" }}>
              Preguntas frecuentes
            </h2>
            <span className="badge-primary">{faqs.length}</span>
          </div>

          <div className="px-6 py-4">
            {loading ? (
              <p className="text-sm" style={{ color: "#888888" }}>
                Cargando FAQs...
              </p>
            ) : error ? (
              <p className="text-sm" style={{ color: "#E53E3E" }}>
                {error}
              </p>
            ) : faqs.length === 0 ? (
              <p className="text-sm" style={{ color: "#888888" }}>
                No hay FAQs todavía.
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr style={{ borderBottom: "1px solid #2A2A2A" }}>
                      {["Pregunta", "Respuesta", "Categoría", ...(isAdmin ? ["Acciones"] : [])].map(
                        (col) => (
                          <th
                            key={col}
                            className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider"
                            style={{ color: "#888888", backgroundColor: "#111111" }}
                          >
                            {col}
                          </th>
                        )
                      )}
                    </tr>
                  </thead>
                  <tbody>
                    {faqs.map((faq) => (
                      <tr
                        key={faq.id}
                        style={{ borderBottom: "1px solid #2A2A2A", transition: "background 0.1s" }}
                        onMouseEnter={(e) =>
                          ((e.currentTarget as HTMLTableRowElement).style.backgroundColor = "#222222")
                        }
                        onMouseLeave={(e) =>
                          ((e.currentTarget as HTMLTableRowElement).style.backgroundColor = "transparent")
                        }
                      >
                        <td className="px-4 py-3 align-top" style={{ color: "#F5F5F5" }}>
                          {faq.question}
                        </td>
                        <td className="px-4 py-3 align-top max-w-sm">
                          <div
                            className="rich-content text-xs"
                            dangerouslySetInnerHTML={{ __html: sanitizeHtml(faq.answer) }}
                          />
                        </td>
                        <td className="px-4 py-3 align-top" style={{ color: "#888888" }}>
                          {faq.category || "General"}
                        </td>
                        {isAdmin && (
                          <td className="px-4 py-3 align-top">
                            <div className="flex gap-3">
                              <button
                                type="button"
                                onClick={() => handleEditClick(faq)}
                                className="text-xs font-medium transition-colors"
                                style={{ color: "#C9A84C" }}
                                onMouseEnter={(e) =>
                                  ((e.currentTarget as HTMLButtonElement).style.color = "#E0B85C")
                                }
                                onMouseLeave={(e) =>
                                  ((e.currentTarget as HTMLButtonElement).style.color = "#C9A84C")
                                }
                              >
                                Editar
                              </button>
                              <button
                                type="button"
                                onClick={() => handleDeleteClick(faq.id, faq.question)}
                                disabled={deleting === faq.id}
                                className="text-xs font-medium transition-colors disabled:opacity-50"
                                style={{ color: "#E53E3E" }}
                              >
                                {deleting === faq.id ? "Borrando..." : "Eliminar"}
                              </button>
                            </div>
                          </td>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Form — solo admin */}
        {isAdmin && (
          <div className="card h-fit">
            <div
              className="flex items-center justify-between border-b px-6 py-4"
              style={{ borderColor: "#2A2A2A" }}
            >
              <h2 className="text-sm font-semibold" style={{ color: "#F5F5F5" }}>
                {editingFaqId ? "Editar FAQ" : "Añadir FAQ"}
              </h2>
              {editingFaqId && (
                <button type="button" onClick={resetForm} className="btn-secondary btn-sm">
                  Cancelar
                </button>
              )}
            </div>

            <div className="px-6 py-4">
              <form className="space-y-4" onSubmit={handleSubmit}>
                <div>
                  <label
                    className="block text-xs font-medium mb-1.5"
                    style={{ color: "#888888" }}
                    htmlFor="question"
                  >
                    Pregunta
                  </label>
                  <input
                    id="question"
                    value={question}
                    onChange={(event) => setQuestion(event.target.value)}
                    className="input"
                    placeholder="Escribe la pregunta"
                  />
                </div>

                <div>
                  <label
                    className="block text-xs font-medium mb-1.5"
                    style={{ color: "#888888" }}
                    htmlFor="answer"
                  >
                    Respuesta
                  </label>
                  <RichEditor
                    content={answer}
                    onChange={setAnswer}
                    placeholder="Escribe la respuesta..."
                    minHeight={140}
                  />
                </div>

                <div>
                  <label
                    className="block text-xs font-medium mb-1.5"
                    style={{ color: "#888888" }}
                    htmlFor="category"
                  >
                    Categoría
                  </label>
                  <input
                    id="category"
                    value={category}
                    onChange={(event) => setCategory(event.target.value)}
                    className="input"
                    placeholder="Categoría (opcional)"
                  />
                </div>

                {error && (
                  <p className="text-xs" style={{ color: "#E53E3E" }}>
                    {error}
                  </p>
                )}

                <button type="submit" disabled={saving} className="btn btn-primary w-full">
                  {saving ? "Guardando..." : editingFaqId ? "Guardar cambios" : "Crear FAQ"}
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
