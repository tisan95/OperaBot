"use client";

import { apiFetch } from "@/lib/api";
import { FormEvent, useEffect, useRef, useState } from "react";
import { Send, MessageSquare, CheckCircle, XCircle, ArrowUpCircle } from "lucide-react";

// ── Types ─────────────────────────────────────────────────────────────────────

interface EscalationFormData {
  intro: string;
  questions: string[];
  context_summary: string;
  originalQuestion: string;
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
      <p className="text-sm" style={{ color: "#888888" }}>
        Formulario enviado.
      </p>
    );
  }

  const allAnswered = answers.every((a) => a.trim().length > 0);

  return (
    <div className="space-y-4">
      <p className="text-sm leading-relaxed" style={{ color: "#F5F5F5" }}>
        {data.intro}
      </p>

      {data.questions.map((q, i) => (
        <div key={i}>
          <label className="block text-xs font-medium mb-1.5" style={{ color: "#888888" }}>
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
    <div className="flex gap-2 mt-3 pt-3 border-t" style={{ borderColor: "#2A2A2A" }}>
      <button
        onClick={() => onResolved(msgId)}
        className="btn btn-sm flex items-center gap-1.5 flex-1 justify-center"
        style={{ backgroundColor: "rgba(56,161,105,0.1)", borderColor: "rgba(56,161,105,0.3)", color: "#38A169", border: "1px solid" }}
      >
        <CheckCircle size={13} strokeWidth={2} />
        Sí, resuelto
      </button>
      <button
        onClick={async () => {
          setEscalating(true);
          await onEscalate(question, msgId);
          setEscalating(false);
        }}
        disabled={escalating}
        className="btn btn-sm flex items-center gap-1.5 flex-1 justify-center"
        style={{ backgroundColor: "rgba(229,62,62,0.08)", borderColor: "rgba(229,62,62,0.25)", color: "#E53E3E", border: "1px solid" }}
      >
        <XCircle size={13} strokeWidth={2} />
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
    <div className="flex gap-2 mt-3 pt-3 border-t" style={{ borderColor: "#2A2A2A" }}>
      <button
        onClick={async () => {
          setEscalating(true);
          await onEscalate(question, msgId);
          setEscalating(false);
        }}
        disabled={escalating}
        className="btn btn-sm flex items-center gap-1.5 flex-1 justify-center"
        style={{ backgroundColor: "rgba(201,168,76,0.1)", borderColor: "rgba(201,168,76,0.3)", color: "#C9A84C", border: "1px solid" }}
      >
        <ArrowUpCircle size={13} strokeWidth={2} />
        {escalating ? "Preparando..." : "Escalar al equipo"}
      </button>
      <button
        onClick={() => onDismiss(msgId)}
        className="btn btn-sm"
        style={{ backgroundColor: "transparent", borderColor: "#2A2A2A", color: "#888888", border: "1px solid" }}
      >
        No, gracias
      </button>
    </div>
  );
}

// ── Main chat component ───────────────────────────────────────────────────────

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionedIds, setActionedIds] = useState<Set<number>>(new Set());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { loadHistory(); }, []);
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const loadHistory = async () => {
    try {
      const data = await apiFetch("/chat/history?limit=50");
      if (Array.isArray(data)) setMessages(data);
    } catch { /* non-critical */ }
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
    if (!userMessage) return;

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
        body: JSON.stringify({ message: userMessage }),
      });
      replaceMsg(tempId, {
        id: resp.id,
        bot_message: resp.bot_message,
        confidence: resp.confidence ?? 0,
        created_at: resp.created_at,
        ui_hint: resp.ui_hint ?? null,
        isLoading: false,
      });
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
    <div
      className="flex flex-col rounded-xl border"
      style={{ height: "calc(100vh - 120px)", backgroundColor: "#0A0A0A", borderColor: "#2A2A2A" }}
    >
      {/* Header */}
      <div
        className="border-b px-6 py-4 shrink-0 flex items-center justify-between"
        style={{ backgroundColor: "#111111", borderColor: "#2A2A2A" }}
      >
        <div>
          <h1 className="text-base font-semibold" style={{ color: "#F5F5F5" }}>Chat</h1>
          <p className="text-xs mt-0.5" style={{ color: "#888888" }}>
            Consulta sobre tu base de conocimiento operacional
          </p>
        </div>
        {hasPendingPrompt && (
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: "#C9A84C" }} />
            <span className="text-xs" style={{ color: "#C9A84C" }}>Valoración pendiente</span>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div
                className="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 border"
                style={{ backgroundColor: "#1A1A1A", borderColor: "#2A2A2A" }}
              >
                <MessageSquare size={20} strokeWidth={1.5} style={{ color: "#C9A84C" }} />
              </div>
              <h2 className="text-base font-semibold mb-2" style={{ color: "#F5F5F5" }}>
                Inicia una conversación
              </h2>
              <p className="text-sm max-w-xs" style={{ color: "#888888" }}>
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
                <div
                  className="max-w-2xl rounded-2xl rounded-br-none px-4 py-3 border"
                  style={{ backgroundColor: "#2A2000", borderColor: "rgba(201,168,76,0.25)", color: "#F5F5F5" }}
                >
                  <p className="text-sm">{msg.user_message}</p>
                </div>
              </div>
            )}

            {/* Bot bubble */}
            <div className="flex justify-start">
              <div
                className="max-w-2xl rounded-2xl rounded-bl-none p-4 border"
                style={{
                  backgroundColor: msg.isRateLimit ? "rgba(201,168,76,0.06)" : "#1A1A1A",
                  borderColor: msg.isRateLimit ? "rgba(201,168,76,0.2)" : "#2A2A2A",
                }}
              >
                {msg.isLoading ? (
                  <div className="flex items-center gap-1.5">
                    {[0, 150, 300].map((d) => (
                      <span
                        key={d}
                        className="w-1.5 h-1.5 rounded-full animate-bounce"
                        style={{ backgroundColor: "#555555", animationDelay: `${d}ms` }}
                      />
                    ))}
                    <span className="text-xs ml-1" style={{ color: "#888888" }}>
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
                    <p
                      className="text-sm leading-relaxed whitespace-pre-wrap"
                      style={{ color: msg.isRateLimit ? "#C9A84C" : "#F5F5F5" }}
                    >
                      {msg.bot_message}
                    </p>

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
            <div
              className="px-4 py-3 rounded-lg border text-sm"
              style={{ backgroundColor: "rgba(229,62,62,0.08)", borderColor: "rgba(229,62,62,0.3)", color: "#E53E3E" }}
            >
              {error}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div
        className="border-t px-6 py-4 shrink-0"
        style={{ borderColor: "#2A2A2A", backgroundColor: "#111111" }}
      >
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Escribe tu pregunta..."
            disabled={loading}
            className="input flex-1"
          />
          <button type="submit" disabled={loading || !input.trim()} className="btn btn-primary gap-2">
            <Send size={14} strokeWidth={2} />
            {loading ? "..." : "Enviar"}
          </button>
        </form>
      </div>
    </div>
  );
}
