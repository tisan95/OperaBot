"use client";

import { apiFetch } from "@/lib/api";
import { FormEvent, useEffect, useRef, useState } from "react";
import { Send, MessageSquare, CheckCircle, XCircle, ArrowUpCircle } from "lucide-react";

interface ChatMessage {
  id: number;
  user_message: string;
  bot_message: string;
  confidence: number;
  created_at: string;
  isLoading?: boolean;
  isRateLimit?: boolean;
  // ui_hint drives action buttons; only present on new messages (not history)
  ui_hint?: "resolution_prompt" | "escalate_prompt" | null;
}

// ── Action buttons ────────────────────────────────────────────────────────────

function ResolutionPrompt({
  msgId,
  question,
  onResolved,
  onEscalate,
}: {
  msgId: number;
  question: string;
  onResolved: (msgId: number) => void;
  onEscalate: (question: string) => Promise<void>;
}) {
  const [escalating, setEscalating] = useState(false);
  return (
    <div className="flex gap-2 mt-3 pt-3 border-t" style={{ borderColor: "#2A2A2A" }}>
      <button
        onClick={() => onResolved(msgId)}
        className="btn btn-sm flex items-center gap-1.5 flex-1 justify-center"
        style={{
          backgroundColor: "rgba(56,161,105,0.1)",
          borderColor: "rgba(56,161,105,0.3)",
          color: "#38A169",
          border: "1px solid",
        }}
      >
        <CheckCircle size={13} strokeWidth={2} />
        Sí, resuelto
      </button>
      <button
        onClick={async () => {
          setEscalating(true);
          await onEscalate(question);
        }}
        disabled={escalating}
        className="btn btn-sm flex items-center gap-1.5 flex-1 justify-center"
        style={{
          backgroundColor: "rgba(229,62,62,0.08)",
          borderColor: "rgba(229,62,62,0.25)",
          color: "#E53E3E",
          border: "1px solid",
        }}
      >
        <XCircle size={13} strokeWidth={2} />
        {escalating ? "Escalando..." : "No me ha servido"}
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
  onEscalate: (question: string) => Promise<void>;
}) {
  const [escalating, setEscalating] = useState(false);
  return (
    <div className="flex gap-2 mt-3 pt-3 border-t" style={{ borderColor: "#2A2A2A" }}>
      <button
        onClick={async () => {
          setEscalating(true);
          await onEscalate(question);
        }}
        disabled={escalating}
        className="btn btn-sm flex items-center gap-1.5 flex-1 justify-center"
        style={{
          backgroundColor: "rgba(201,168,76,0.1)",
          borderColor: "rgba(201,168,76,0.3)",
          color: "#C9A84C",
          border: "1px solid",
        }}
      >
        <ArrowUpCircle size={13} strokeWidth={2} />
        {escalating ? "Escalando..." : "Escalar al equipo"}
      </button>
      <button
        onClick={() => onDismiss(msgId)}
        className="btn btn-sm flex items-center gap-1.5"
        style={{
          backgroundColor: "transparent",
          borderColor: "#2A2A2A",
          color: "#888888",
          border: "1px solid",
        }}
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
  // Track message IDs where the user has already acted (resolved / escalated / dismissed)
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
    } catch {
      // history load failure is non-critical
    }
  };

  const addMessage = (msg: ChatMessage) =>
    setMessages((prev) => [...prev, msg]);

  const replaceTemp = (tempId: number, replacement: Partial<ChatMessage> & { id: number }) =>
    setMessages((prev) => prev.map((m) => (m.id === tempId ? { ...m, ...replacement } : m)));

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const userMessage = input.trim();
    if (!userMessage) return;

    setError(null);
    setInput("");
    setLoading(true);

    const tempId = Date.now() * -1; // negative to avoid collision with real IDs
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
      replaceTemp(tempId, {
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
        replaceTemp(tempId, {
          id: Math.abs(tempId),
          bot_message: msg,
          confidence: 0,
          created_at: new Date().toISOString(),
          isRateLimit: true,
          isLoading: false,
        });
      } else {
        setError(msg);
        setMessages((prev) => prev.filter((m) => m.id !== tempId));
      }
    } finally {
      setLoading(false);
    }
  };

  const markActioned = (msgId: number) =>
    setActionedIds((prev) => new Set(prev).add(msgId));

  const handleResolved = (msgId: number) => {
    markActioned(msgId);
    // Add a synthetic "resolved" bot message
    addMessage({
      id: Date.now(),
      user_message: "Sí, está resuelto",
      bot_message: "Me alegra haberte ayudado. Si tienes alguna otra duda, aquí estaré.",
      confidence: 1,
      created_at: new Date().toISOString(),
    });
  };

  const handleEscalate = async (question: string) => {
    try {
      const resp = await apiFetch("/chat/escalate", {
        method: "POST",
        body: JSON.stringify({ question }),
      });
      // Mark all pending prompts as actioned
      setActionedIds((prev) => {
        const next = new Set(prev);
        messages.forEach((m) => { if (m.ui_hint) next.add(m.id); });
        return next;
      });
      addMessage({
        id: Date.now(),
        user_message: "Escalar mi consulta",
        bot_message: resp.message || "Tu consulta ha sido escalada al equipo.",
        confidence: 1,
        created_at: new Date().toISOString(),
      });
    } catch (err: any) {
      setError(err.message || "Error al escalar la consulta");
    }
  };

  // Whether there's any unactioned resolution_prompt (for header indicator)
  const hasPendingPrompt = messages.some(
    (m) => m.ui_hint === "resolution_prompt" && !actionedIds.has(m.id)
  );

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
            {/* User bubble */}
            <div className="flex justify-end">
              <div
                className="max-w-2xl rounded-2xl rounded-br-none px-4 py-3 border"
                style={{ backgroundColor: "#2A2000", borderColor: "rgba(201,168,76,0.25)", color: "#F5F5F5" }}
              >
                <p className="text-sm">{msg.user_message}</p>
              </div>
            </div>

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
                    {[0, 150, 300].map((delay) => (
                      <span
                        key={delay}
                        className="w-1.5 h-1.5 rounded-full animate-bounce"
                        style={{ backgroundColor: "#555555", animationDelay: `${delay}ms` }}
                      />
                    ))}
                    <span className="text-xs ml-1" style={{ color: "#888888" }}>Procesando...</span>
                  </div>
                ) : (
                  <>
                    <p
                      className="text-sm leading-relaxed whitespace-pre-wrap"
                      style={{ color: msg.isRateLimit ? "#C9A84C" : "#F5F5F5" }}
                    >
                      {msg.bot_message}
                    </p>

                    {/* Action buttons — only if not already actioned */}
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
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="btn btn-primary gap-2"
          >
            <Send size={14} strokeWidth={2} />
            {loading ? "..." : "Enviar"}
          </button>
        </form>
      </div>
    </div>
  );
}
