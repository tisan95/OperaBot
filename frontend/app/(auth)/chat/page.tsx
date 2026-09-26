"use client";

import { apiFetch } from "@/lib/api";
import { useAuthContext } from "@/components/Auth/AuthProvider";
import DocumentPreview from "@/components/Shared/DocumentPreview";
import SessionsDropdown, { ChatSession } from "@/components/Chat/SessionsDropdown";
import { FormEvent, useEffect, useRef, useState } from "react";
import { Send, MessageSquare, CheckCircle, XCircle, ArrowUpCircle, Info } from "lucide-react";

const MAX_ACTIVE_SESSIONS = 5;

// ── Types ─────────────────────────────────────────────────────────────────────

interface EscalationFormData {
  intro: string;
  questions: string[];
  context_summary: string;
  originalQuestion: string;
}

interface CitedDocument {
  id: string;
  name: string;
}

interface ChatMessage {
  id: number;
  user_message: string;
  bot_message: string;
  confidence: number;
  created_at: string;
  isLoading?: boolean;
  isRateLimit?: boolean;
  ui_hint?: "resolution_prompt" | "escalate_prompt" | null;
  cited_documents?: CitedDocument[];
  // Escalation form embedded in the chat
  isEscalationForm?: true;
  escalationForm?: EscalationFormData;
  escalationFormDone?: boolean;
}

// ── EscalationForm ────────────────────────────────────────────────────────────

function EscalationForm({
  msgId,
  data,
  done,
  onSubmit,
  onCancel,
}: {
  msgId: number;
  data: EscalationFormData;
  done: boolean;
  onSubmit: (msgId: number, answers: string[]) => Promise<void>;
  onCancel: (msgId: number) => void;
}) {
  const [answers, setAnswers] = useState<string[]>(data.questions.map(() => ""));
  const [submitting, setSubmitting] = useState(false);

  if (done) {
    return (
      <p className="text-sm text-text-secondary">
        Formulario enviado.
      </p>
    );
  }

  const allAnswered = answers.every((a) => a.trim().length > 0);

  return (
    <div className="space-y-4">
      <p className="text-sm leading-relaxed text-text-primary">
        {data.intro}
      </p>

      {data.questions.map((q, i) => (
        <div key={i}>
          <label className="block text-xs font-medium mb-1.5 text-text-secondary">
            {q}
          </label>
          <textarea
            value={answers[i]}
            onChange={(e) => {
              const next = [...answers];
              next[i] = e.target.value;
              setAnswers(next);
            }}
            disabled={submitting}
            className="input w-full resize-none"
            rows={2}
            placeholder="Tu respuesta..."
          />
        </div>
      ))}

      <div className="flex gap-2">
        <button
          onClick={async () => {
            setSubmitting(true);
            await onSubmit(msgId, answers);
            setSubmitting(false);
          }}
          disabled={submitting || !allAnswered}
          className="btn btn-primary flex-1"
        >
          {submitting ? "Enviando..." : "Enviar y escalar"}
        </button>
        <button
          onClick={() => onCancel(msgId)}
          disabled={submitting}
          className="btn btn-secondary"
        >
          Cancelar
        </button>
      </div>
    </div>
  );
}

// ── Resolution / Escalate buttons ─────────────────────────────────────────────

function ResolutionPrompt({
  msgId,
  question,
  onResolved,
  onEscalate,
}: {
  msgId: number;
  question: string;
  onResolved: (msgId: number) => void;
  onEscalate: (question: string, sourceMsgId: number) => Promise<void>;
}) {
  const [escalating, setEscalating] = useState(false);
  return (
    <div className="flex gap-2 mt-3 pt-3 border-t border-border">
      <button
        onClick={() => onResolved(msgId)}
        className="btn btn-sm flex items-center gap-1.5 flex-1 justify-center border bg-success/10 border-success/30 text-success"
      >
        <CheckCircle size={13} strokeWidth={1.5} />
        Sí, resuelto
      </button>
      <button
        onClick={async () => {
          setEscalating(true);
          await onEscalate(question, msgId);
          setEscalating(false);
        }}
        disabled={escalating}
        className="btn btn-sm flex items-center gap-1.5 flex-1 justify-center border bg-error/8 border-error/25 text-error"
      >
        <XCircle size={13} strokeWidth={1.5} />
        {escalating ? "Preparando..." : "No me ha servido"}
      </button>
    </div>
  );
}

function EscalatePrompt({
  msgId,
  question,
  onDismiss,
  onEscalate,
}: {
  msgId: number;
  question: string;
  onDismiss: (msgId: number) => void;
  onEscalate: (question: string, sourceMsgId: number) => Promise<void>;
}) {
  const [escalating, setEscalating] = useState(false);
  return (
    <div className="flex gap-2 mt-3 pt-3 border-t border-border">
      <button
        onClick={async () => {
          setEscalating(true);
          await onEscalate(question, msgId);
          setEscalating(false);
        }}
        disabled={escalating}
        className="btn btn-sm flex items-center gap-1.5 flex-1 justify-center border bg-gold/10 border-gold/30 text-gold"
      >
        <ArrowUpCircle size={13} strokeWidth={1.5} />
        {escalating ? "Preparando..." : "Escalar al equipo"}
      </button>
      <button
        onClick={() => onDismiss(msgId)}
        className="btn btn-sm border border-border text-text-secondary"
      >
        No, gracias
      </button>
    </div>
  );
}

// ── Main chat component ───────────────────────────────────────────────────────

export default function ChatPage() {
  const { user } = useAuthContext();
  const userRole = user?.role ?? "user";

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionedIds, setActionedIds] = useState<Set<number>>(new Set());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // ── Session state ──
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null);
  const [initializing, setInitializing] = useState(true);
  const [archiveNotice, setArchiveNotice] = useState<string | null>(null);

  useEffect(() => { initSession(); }, []);
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const showArchiveNotice = () => {
    setArchiveNotice("Se ha archivado tu conversación más antigua por límite de 5 activas.");
    setTimeout(() => setArchiveNotice(null), 5000);
  };

  // ── Session lifecycle ──

  const initSession = async () => {
    setInitializing(true);
    try {
      const list = await apiFetch("/chat/sessions");
      const active: ChatSession[] = Array.isArray(list) ? list : [];
      if (active.length > 0) {
        setSessions(active);
        await selectSession(active[0].id);
      } else {
        const created = await apiFetch("/chat/sessions", { method: "POST" });
        setSessions([created]);
        setActiveSessionId(created.id);
        setMessages([]);
      }
    } catch (err: any) {
      setError(err.message || "Error al iniciar el chat");
    } finally {
      setInitializing(false);
    }
  };

  const selectSession = async (sessionId: number) => {
    setActiveSessionId(sessionId);
    setActionedIds(new Set());
    setError(null);
    try {
      const msgs = await apiFetch(`/chat/sessions/${sessionId}/messages`);
      setMessages(Array.isArray(msgs) ? msgs : []);
    } catch (err: any) {
      setMessages([]);
      setError(err.message || "Error al cargar la conversación");
    }
  };

  const refreshSessions = async () => {
    try {
      const list = await apiFetch("/chat/sessions");
      if (Array.isArray(list)) setSessions(list);
    } catch { /* non-critical */ }
  };

  const handleNewSession = async () => {
    const wasAtLimit = sessions.length >= MAX_ACTIVE_SESSIONS;
    try {
      const created = await apiFetch("/chat/sessions", { method: "POST" });
      setActiveSessionId(created.id);
      setMessages([]);
      setActionedIds(new Set());
      setError(null);
      await refreshSessions();
      if (wasAtLimit) showArchiveNotice();
    } catch (err: any) {
      setError(err.message || "Error al crear la conversación");
    }
  };

  const handleDeleteSession = async (sessionId: number) => {
    try {
      await apiFetch(`/chat/sessions/${sessionId}`, { method: "DELETE" });
      const list = await apiFetch("/chat/sessions");
      const active: ChatSession[] = Array.isArray(list) ? list : [];
      setSessions(active);
      if (sessionId === activeSessionId) {
        if (active.length > 0) {
          await selectSession(active[0].id);
        } else {
          const created = await apiFetch("/chat/sessions", { method: "POST" });
          setSessions([created]);
          setActiveSessionId(created.id);
          setMessages([]);
        }
      }
    } catch (err: any) {
      setError(err.message || "Error al borrar la conversación");
    }
  };

  const addMessage = (msg: ChatMessage) =>
    setMessages((prev) => [...prev, msg]);

  const replaceMsg = (id: number, patch: Partial<ChatMessage>) =>
    setMessages((prev) => prev.map((m) => (m.id === id ? { ...m, ...patch } : m)));

  const removeMsg = (id: number) =>
    setMessages((prev) => prev.filter((m) => m.id !== id));

  const markActioned = (msgId: number) =>
    setActionedIds((prev) => new Set(prev).add(msgId));

  // ── Send message ──

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const userMessage = input.trim();
    if (!userMessage || !activeSessionId) return;

    setError(null);
    setInput("");
    setLoading(true);

    const tempId = Date.now() * -1;
    addMessage({
      id: tempId,
      user_message: userMessage,
      bot_message: "",
      confidence: 0,
      created_at: new Date().toISOString(),
      isLoading: true,
    });

    try {
      const resp = await apiFetch("/chat/messages", {
        method: "POST",
        body: JSON.stringify({ message: userMessage, session_id: activeSessionId }),
      });
      replaceMsg(tempId, {
        id: resp.id,
        bot_message: resp.bot_message,
        confidence: resp.confidence ?? 0,
        created_at: resp.created_at,
        ui_hint: resp.ui_hint ?? null,
        cited_documents: resp.cited_documents ?? [],
        isLoading: false,
      });
      refreshSessions();
    } catch (err: any) {
      const isRateLimit = err?.status === 429;
      const msg = err instanceof Error ? err.message : "Error al enviar el mensaje";
      if (isRateLimit) {
        replaceMsg(tempId, {
          id: Math.abs(tempId),
          bot_message: msg,
          confidence: 0,
          created_at: new Date().toISOString(),
          isRateLimit: true,
          isLoading: false,
        });
      } else {
        setError(msg);
        removeMsg(tempId);
      }
    } finally {
      setLoading(false);
    }
  };

  // ── Resolved ──

  const handleResolved = (msgId: number) => {
    markActioned(msgId);
    addMessage({
      id: Date.now(),
      user_message: "Sí, está resuelto",
      bot_message: "Me alegra haberte ayudado. Si tienes alguna otra duda, aquí estaré.",
      confidence: 1,
      created_at: new Date().toISOString(),
    });
  };

  // ── Escalate: step 1 — fetch questions from LLM ──

  const handleEscalate = async (question: string, sourceMsgId: number) => {
    markActioned(sourceMsgId);

    const formId = Date.now() * -1;
    addMessage({
      id: formId,
      user_message: "",
      bot_message: "",
      confidence: 0,
      created_at: new Date().toISOString(),
      isLoading: true,
    });

    try {
      const data = await apiFetch("/chat/escalate-questions", { method: "POST" });
      replaceMsg(formId, {
        id: formId,
        isLoading: false,
        isEscalationForm: true,
        escalationForm: {
          intro: data.intro,
          questions: data.questions,
          context_summary: data.context_summary,
          originalQuestion: question,
        },
        escalationFormDone: false,
      });
    } catch (err: any) {
      removeMsg(formId);
      setError(err.message || "Error al preparar el escalado");
    }
  };

  // ── Escalate: step 2 — submit form with answers ──

  const handleEscalationSubmit = async (formMsgId: number, answers: string[]) => {
    const formMsg = messages.find((m) => m.id === formMsgId);
    if (!formMsg?.escalationForm) return;

    try {
      const resp = await apiFetch("/chat/escalate", {
        method: "POST",
        body: JSON.stringify({
          question: formMsg.escalationForm.originalQuestion,
          answers,
          context_summary: formMsg.escalationForm.context_summary,
        }),
      });

      replaceMsg(formMsgId, { escalationFormDone: true });

      addMessage({
        id: Date.now(),
        user_message: "Enviar y escalar",
        bot_message: resp.message || "Consulta escalada al equipo.",
        confidence: 1,
        created_at: new Date().toISOString(),
      });
    } catch (err: any) {
      setError(err.message || "Error al escalar la consulta");
    }
  };

  const handleEscalationCancel = (formMsgId: number) => removeMsg(formMsgId);

  const hasPendingPrompt = messages.some(
    (m) => m.ui_hint === "resolution_prompt" && !actionedIds.has(m.id)
  );

  // ── Render ──

  return (
    <div className="flex flex-col flex-1 min-h-0 rounded-xl border bg-bg border-border">
      {/* Header */}
      <div className="border-b px-6 py-4 shrink-0 flex items-center justify-between bg-surface border-border">
        <div>
          <h1 className="text-base font-semibold text-text-primary">Chat</h1>
          <p className="text-xs mt-0.5 text-text-secondary">
            Consulta sobre tu base de conocimiento operacional
          </p>
        </div>
        <div className="flex items-center gap-3">
          {hasPendingPrompt && (
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-gold" />
              <span className="text-xs text-gold">Valoración pendiente</span>
            </div>
          )}
          <SessionsDropdown
            sessions={sessions}
            activeSessionId={activeSessionId}
            onOpen={refreshSessions}
            onSelect={selectSession}
            onNew={handleNewSession}
            onDelete={handleDeleteSession}
          />
        </div>
      </div>

      {/* Archive notice toast */}
      {archiveNotice && (
        <div className="px-6 pt-3 shrink-0">
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg border text-xs bg-gold/8 border-gold/25 text-gold animate-fadeIn">
            <Info size={13} strokeWidth={1.5} />
            {archiveNotice}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
        {initializing ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-sm text-text-secondary">Cargando conversación...</p>
          </div>
        ) : messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 border bg-card border-border">
                <MessageSquare size={20} strokeWidth={1.5} className="text-gold" />
              </div>
              <h2 className="text-base font-semibold mb-2 text-text-primary">
                Inicia una conversación
              </h2>
              <p className="text-sm max-w-xs text-text-secondary">
                Pregunta sobre procedimientos, manuales o preguntas frecuentes.
              </p>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className="space-y-3 animate-fadeIn">
            {/* User bubble — skip for escalation form placeholder messages */}
            {msg.user_message && !msg.isEscalationForm && (
              <div className="flex justify-end">
                <div className="max-w-2xl rounded-2xl rounded-br-none px-4 py-3 border bg-gold-dark border-gold/25 text-text-primary">
                  <p className="text-sm">{msg.user_message}</p>
                </div>
              </div>
            )}

            {/* Bot bubble */}
            <div className="flex justify-start">
              <div
                className={`max-w-2xl rounded-2xl rounded-bl-none p-4 border ${
                  msg.isRateLimit
                    ? "bg-gold/6 border-gold/20"
                    : "bg-card border-border border-l-[3px] border-l-gold"
                }`}
              >
                {msg.isLoading ? (
                  <div className="flex items-center gap-1.5">
                    {[0, 150, 300].map((d) => (
                      <span
                        key={d}
                        className="w-1.5 h-1.5 rounded-full animate-bounce bg-muted"
                        style={{ animationDelay: `${d}ms` }}
                      />
                    ))}
                    <span className="text-xs ml-1 text-text-secondary">
                      {msg.isEscalationForm ? "Analizando tu consulta..." : "Procesando..."}
                    </span>
                  </div>
                ) : msg.isEscalationForm && msg.escalationForm ? (
                  <EscalationForm
                    msgId={msg.id}
                    data={msg.escalationForm}
                    done={!!msg.escalationFormDone}
                    onSubmit={handleEscalationSubmit}
                    onCancel={handleEscalationCancel}
                  />
                ) : (
                  <>
                    <p className={`text-sm leading-relaxed whitespace-pre-wrap ${msg.isRateLimit ? "text-gold" : "text-text-primary"}`}>
                      {msg.bot_message}
                    </p>

                    {/* Cited documents — PDF preview cards */}
                    {msg.cited_documents && msg.cited_documents.length > 0 && (
                      <div className="mt-3 space-y-1">
                        {msg.cited_documents.map((doc) => (
                          <DocumentPreview
                            key={doc.id}
                            document_id={doc.id}
                            document_name={doc.name}
                            user_role={userRole}
                          />
                        ))}
                      </div>
                    )}

                    {!actionedIds.has(msg.id) && msg.ui_hint === "resolution_prompt" && (
                      <ResolutionPrompt
                        msgId={msg.id}
                        question={msg.user_message}
                        onResolved={handleResolved}
                        onEscalate={handleEscalate}
                      />
                    )}
                    {!actionedIds.has(msg.id) && msg.ui_hint === "escalate_prompt" && (
                      <EscalatePrompt
                        msgId={msg.id}
                        question={msg.user_message}
                        onDismiss={markActioned}
                        onEscalate={handleEscalate}
                      />
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        ))}

        {error && (
          <div className="flex justify-center">
            <div className="px-4 py-3 rounded-lg border text-sm bg-error/8 border-error/30 text-error">
              {error}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t px-6 py-4 shrink-0 border-border bg-surface">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Escribe tu pregunta..."
            disabled={loading || initializing}
            className="input flex-1"
          />
          <button type="submit" disabled={loading || initializing || !input.trim()} className="btn btn-primary gap-2">
            <Send size={14} strokeWidth={1.5} />
            {loading ? "..." : "Enviar"}
          </button>
        </form>
      </div>
    </div>
  );
}
