"use client";

import { apiFetch } from "@/lib/api";
import { FAQ } from "@/lib/types";
import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
// IMPORTAMOS EL CONTEXTO
import { useAuthContext } from "@/components/Auth/AuthProvider";

export default function FAQPage() {
  // EXTRAEMOS EL USUARIO
  const { user } = useAuthContext();
  const isAdmin = user?.role === "admin"; // Variable auxiliar súper útil

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
      await apiFetch(`/faqs/${faqId}`, {
        method: "DELETE",
      });

      // Remove from UI immediately
      setFaqs(faqs.filter((faq) => faq.id !== faqId));
      
      // If we were editing this FAQ, reset the form
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
    <div className="min-h-screen bg-slate-50">
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div>
            <Link
              href="/dashboard"
              className="text-sm text-sky-600 hover:underline"
            >
              ← Back to dashboard
            </Link>
            <h1 className="mt-2 text-3xl font-semibold text-slate-900">
              FAQ Browser
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              Browse, add, and maintain your operational knowledge.
            </p>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">
        {/* MAGIA AQUÍ: Si es admin divide en 2 columnas, si no, usa solo 1 */}
        <div className={`grid gap-6 ${isAdmin ? 'lg:grid-cols-[1.6fr_1fr]' : 'lg:grid-cols-1'}`}>
          
          <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-100 px-6 py-4">
              <h2 className="text-lg font-semibold text-slate-900">FAQs</h2>
            </div>

            <div className="px-6 py-4">
              {loading ? (
                <p className="text-slate-600">Loading FAQs...</p>
              ) : error ? (
                <p className="text-red-600">{error}</p>
              ) : faqs.length === 0 ? (
                <p className="text-slate-600">No FAQs found yet.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-slate-200 text-sm">
                    <thead className="bg-slate-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                          Question
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                          Answer
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                          Category
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                          Created
                        </th>
                        {/* Ocultamos cabecera de Acciones si no es admin */}
                        {isAdmin && (
                          <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                            Actions
                          </th>
                        )}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200 bg-white">
                      {faqs.map((faq) => (
                        <tr key={faq.id}>
                          <td className="px-4 py-3 align-top text-slate-900">
                            {faq.question}
                          </td>
                          <td className="px-4 py-3 align-top text-slate-700">
                            {faq.answer}
                          </td>
                          <td className="px-4 py-3 align-top text-slate-700">
                            {faq.category || "General"}
                          </td>
                          <td className="px-4 py-3 align-top text-slate-500">
                            {new Date(faq.created_at).toLocaleString()}
                          </td>
                          {/* Ocultamos los botones de editar/borrar si no es admin */}
                          {isAdmin && (
                            <td className="px-4 py-3 align-top text-right space-x-3">
                              <button
                                type="button"
                                onClick={() => handleEditClick(faq)}
                                className="text-sm font-medium text-sky-600 hover:text-sky-800"
                              >
                                Edit
                              </button>
                              <button
                                type="button"
                                onClick={() => handleDeleteClick(faq.id, faq.question)}
                                disabled={deleting === faq.id}
                                className="text-sm font-medium text-red-600 hover:text-red-800 disabled:opacity-50"
                              >
                                {deleting === faq.id ? "Deleting..." : "Delete"}
                              </button>
                            </td>
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </section>

          {/* Ocultamos el bloque de creación entero si no es admin */}
          {isAdmin && (
            <section className="rounded-xl border border-slate-200 bg-white shadow-sm h-fit">
              <div className="border-b border-slate-100 px-6 py-4">
                <div className="flex items-center justify-between gap-4">
                  <h2 className="text-lg font-semibold text-slate-900">
                    {editingFaqId ? "Edit FAQ" : "Add FAQ"}
                  </h2>
                  {editingFaqId ? (
                    <button
                      type="button"
                      onClick={resetForm}
                      className="rounded-md bg-slate-100 px-3 py-2 text-sm text-slate-700 hover:bg-slate-200"
                    >
                      Cancel edit
                    </button>
                  ) : null}
                </div>
              </div>
              <div className="px-6 py-4">
                <form className="space-y-4" onSubmit={handleSubmit}>
                  <div>
                    <label
                      className="mb-1 block text-sm font-medium text-slate-700"
                      htmlFor="question"
                    >
                      Question
                    </label>
                    <input
                      id="question"
                      value={question}
                      onChange={(event) => setQuestion(event.target.value)}
                      className="block w-full rounded-md border-slate-300 text-sm shadow-sm focus:border-sky-500 focus:ring-sky-500"
                      placeholder="Enter a common question"
                    />
                  </div>

                  <div>
                    <label
                      className="mb-1 block text-sm font-medium text-slate-700"
                      htmlFor="answer"
                    >
                      Answer
                    </label>
                    <textarea
                      id="answer"
                      value={answer}
                      onChange={(event) => setAnswer(event.target.value)}
                      className="block w-full rounded-md border-slate-300 text-sm shadow-sm focus:border-sky-500 focus:ring-sky-500"
                      rows={4}
                      placeholder="Enter the answer"
                    />
                  </div>

                  <div>
                    <label
                      className="mb-1 block text-sm font-medium text-slate-700"
                      htmlFor="category"
                    >
                      Category
                    </label>
                    <input
                      id="category"
                      value={category}
                      onChange={(event) => setCategory(event.target.value)}
                      className="block w-full rounded-md border-slate-300 text-sm shadow-sm focus:border-sky-500 focus:ring-sky-500"
                      placeholder="Optional category"
                    />
                  </div>

                  {error && (
                    <p className="text-sm text-red-600">{error}</p>
                  )}

                  <button
                    type="submit"
                    disabled={saving}
                    className="inline-flex w-full items-center justify-center rounded-md bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-sky-300"
                  >
                    {saving ? "Saving..." : editingFaqId ? "Save changes" : "Create FAQ"}
                  </button>
                </form>
              </div>
            </section>
          )}
        </div>
      </main>
    </div>
  );
}